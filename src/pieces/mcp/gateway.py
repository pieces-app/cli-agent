"""
MCP Gateway -- stdio-to-PiecesOS bridge.

Implements the gateway that sits between IDE clients (communicating via stdio)
and PiecesOS (communicating via streamable HTTP or SSE). The gateway proxies
tool discovery and tool calls, handles reconnection, and validates system
status before each operation.

Architecture::

    IDE (Claude, Cursor, ...) <--stdio--> MCPGateway <--streamable HTTP--> PiecesOS

Key classes:
    PosMcpConnection  -- manages the upstream connection to PiecesOS
    MCPGateway        -- stdio server that routes IDE requests to PiecesOS
"""

import asyncio
import hashlib
import re
import signal
import threading
from typing import Any, Awaitable, Callable

import httpcore
import httpx
import sentry_sdk
from pydantic import ValidationError

from websocket import WebSocketConnectionClosedException
from pieces.mcp.utils import get_mcp_latest_url, invalidate_mcp_url_cache
from pieces.mcp.tools_cache import PIECES_MCP_TOOLS_CACHE
from pieces.settings import Settings
from .._vendor.pieces_os_client.wrapper.version_compatibility import (
    UpdateEnum,
    VersionChecker,
)
from .._vendor.pieces_os_client.wrapper.websockets.health_ws import HealthWS
from .._vendor.pieces_os_client.wrapper.websockets.ltm_vision_ws import LTMVisionWS
from .._vendor.pieces_os_client.wrapper.websockets.auth_ws import AuthWS
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions


class PosMcpConnection:
    """Manages the upstream connection to the PiecesOS MCP server.

    Handles the full connection lifecycle: establishing a streamable HTTP
    transport, creating a ``ClientSession``, discovering tools, handling
    reconnection on failure, and cleaning up resources.

    Thread-safety:
        * ``connection_lock`` (asyncio.Lock) serialises connect/cleanup calls.
        * ``_health_check_lock`` (asyncio.Lock) guards the async PiecesOS
          health check.  Blocking SDK calls are wrapped in
          ``asyncio.to_thread()`` to avoid stalling the event loop.

    Error surfacing:
        Connection errors are stored in ``_last_connection_error`` so that
        the next ``call_tool`` invocation can include them in the user-facing
        response instead of returning a generic message.
    """

    def __init__(
        self, upstream_url: str | None, tools_changed_callback: Callable[[], Awaitable[None]]
    ):
        self.upstream_url: str | None = upstream_url
        self.CONNECTION_ESTABLISH_ATTEMPTS: int = 100
        self.CONNECTION_CHECK_INTERVAL: float = 0.1
        self.session: ClientSession | None = None
        self._transport_ctx: object | None = None
        self.discovered_tools: list[types.Tool] = []
        self.connection_lock: asyncio.Lock = asyncio.Lock()
        self._pieces_os_running: bool | None = None
        self._ltm_enabled: bool | None = None
        self.result: object | None = None
        self._previous_tools_hash: str | None = None
        self._tools_changed_callback: Callable[[], Awaitable[None]] = tools_changed_callback
        self._health_check_lock: asyncio.Lock = asyncio.Lock()
        self._last_connection_error: str | None = None
        self._upstream_session_id: str | None = None

        self._cleanup_requested: asyncio.Event = asyncio.Event()
        self._connection_task: asyncio.Task | None = None
        self._event_loop: asyncio.AbstractEventLoop | None = None

    def _try_get_upstream_url(self) -> bool:
        """Try to resolve the upstream URL if we don't have one yet.

        Invalidates the URL cache before fetching so that a PiecesOS restart
        on a different port is handled correctly.

        Returns:
            True if ``self.upstream_url`` is set, False otherwise.
        """
        if self.upstream_url is None:
            if Settings.pieces_client.is_pieces_running():
                try:
                    invalidate_mcp_url_cache()
                    self.upstream_url = get_mcp_latest_url()
                    return True
                except Exception as e:
                    Settings.logger.warning(f"Failed to get MCP upstream URL: {e}")
            return False
        return True

    def request_cleanup(self) -> None:
        """Request cleanup from exception handler (thread-safe).

        Uses the stored ``_event_loop`` reference rather than
        ``asyncio.get_running_loop()`` because this method is invoked
        from WebSocket callback threads where no asyncio loop is running.
        """
        Settings.logger.debug("Cleanup requested from exception handler")

        loop = self._event_loop
        if loop is None:
            Settings.logger.debug("No event loop stored yet for cleanup request")
            return

        if not loop.is_closed():
            loop.call_soon_threadsafe(self._schedule_cleanup)

    def _schedule_cleanup(self) -> None:
        """Internal method to schedule cleanup in the event loop."""
        self._cleanup_requested.set()

        if self._connection_task and not self._connection_task.done():
            self._connection_task.cancel()
            Settings.logger.debug("Connection task cancelled due to cleanup request")

    async def _cleanup_stale_session(self) -> None:
        """Clean up a stale session and its resources.

        Ordering guarantee: ``__aexit__`` is called on the session and
        transport context *before* the instance variables are nullified.
        This prevents a concurrent ``connect()`` from seeing ``None`` and
        starting a new connection while old resources are still tearing down.
        """
        session = self.session
        transport_ctx = self._transport_ctx

        if session:
            try:
                await session.__aexit__(None, None, None)
                Settings.logger.debug("Session cleaned up successfully")
            except Exception as e:
                Settings.logger.debug(f"Error cleaning up session: {e}")

        if transport_ctx:
            try:
                await transport_ctx.__aexit__(None, None, None)
                Settings.logger.debug("Transport context cleaned up successfully")
            except Exception as e:
                Settings.logger.debug(f"Error cleaning up transport context: {e}")

        self.session = None
        self._transport_ctx = None
        self._upstream_session_id = None
        self.discovered_tools = []

        invalidate_mcp_url_cache()

    def _check_version_compatibility(self) -> tuple[bool, str]:
        """Check if the PiecesOS version is compatible with the MCP server.

        Returns:
            ``(True, "")`` if compatible, ``(False, message)`` otherwise.
            The message includes actionable remediation steps for the user.
        """
        version = Settings.pieces_client.version
        if version == "debug":
            return True, ""
        if not self.result:
            self.result = VersionChecker(
                Settings.PIECES_OS_MIN_VERSION,
                Settings.PIECES_OS_MAX_VERSION,
                version,
            ).version_check()

        if self.result.compatible:
            return True, ""

        if self.result.update == UpdateEnum.Plugin:
            return (
                False,
                "Please update the CLI version to be able to run the tool call, Run 'pieces manage update' to get the latest version. Then retry your request again after updating.",
            )
        else:
            return (
                False,
                "Please update PiecesOS to a compatible version to be able to run the tool call. Run 'pieces update' to get the latest version. Then retry your request again after updating.",
            )

    async def _check_pieces_os_status(self) -> bool:
        """Check if PiecesOS is running and initialise health state.

        Two-phase check (both under ``_health_check_lock``):
            1. **Fast path**: if the health WebSocket is already running,
               return immediately.
            2. **Slow path**: call blocking SDK methods (``is_pieces_running``,
               ``health_ws.start``, ``user_snapshot``, etc.) via
               ``asyncio.to_thread()`` so the event loop is never stalled.

        The lock covers the entire method so that only one coroutine runs
        the slow-path probe at a time, preventing redundant health-WS
        starts and shared-state races.

        Returns:
            True if PiecesOS is healthy and reachable, False otherwise.
        """
        async with self._health_check_lock:
            if HealthWS.is_running() and Settings.pieces_client.is_pos_stream_running:
                return True

            is_running = await asyncio.to_thread(
                Settings.pieces_client.is_pieces_running, 2
            )
            if not is_running:
                return False

            try:
                health_ws = HealthWS.get_instance()
                if health_ws:
                    await asyncio.to_thread(health_ws.start)

                os_id = await asyncio.to_thread(Settings.get_os_id)
                sentry_sdk.set_user({"id": os_id or "unknown"})

                snapshot = await asyncio.to_thread(
                    Settings.pieces_client.user_api.user_snapshot
                )
                Settings.pieces_client.user.user_profile = snapshot.user

                ltm_status = await asyncio.to_thread(
                    Settings.pieces_client.work_stream_pattern_engine_api
                    .workstream_pattern_engine_processors_vision_status
                )
                Settings.pieces_client.copilot.context.ltm.ltm_status = ltm_status

                invalidate_mcp_url_cache()
                return True
            except Exception as e:
                Settings.logger.warning(
                    f"PiecesOS appears to be running but health check failed: {e}"
                )
                return False

    def _check_ltm_status(self) -> bool:
        """Check if LTM is enabled."""
        return Settings.pieces_client.copilot.context.ltm.is_enabled

    async def _validate_system_status(self, tool_name: str) -> tuple[bool, str]:
        """Perform 4-step validation before executing any tool.

        Steps:
            1. Check PiecesOS health (via WebSocket)
            2. Check version compatibility (CLI vs PiecesOS)
            3. Check user authentication
            4. Check LTM status (for LTM-specific tools only)

        Returns:
            ``(is_valid, error_message)`` -- error_message includes actionable
            remediation steps when ``is_valid`` is False.
        """
        if not await self._check_pieces_os_status():
            return False, (
                "PiecesOS is not running. To use this tool, please run:\n\n"
                "`pieces open`\n\n"
                "This will start PiecesOS, then you can retry your request."
            )

        is_compatible, compatibility_message = self._check_version_compatibility()
        if not is_compatible:
            return False, compatibility_message

        if not Settings.pieces_client.user.user_profile:
            return False, (
                "User must sign up to use this tool, please run:\n\n`pieces login`\n\n"
                "This will open the authentication page in your browser. After signing in, you can retry your request."
            )

        if tool_name in ["ask_pieces_ltm", "create_pieces_memory"]:
            ltm_enabled = self._check_ltm_status()
            if not ltm_enabled:
                return False, (
                    "PiecesOS is running but Long Term Memory (LTM) is not enabled. "
                    "To use this tool, please run:\n\n"
                    "`pieces open --ltm`\n\n"
                    "This will enable LTM, then you can retry your request."
                )

        return True, ""

    async def _get_error_message_for_tool(self, tool_name: str) -> str:
        """Get an actionable error message based on the tool and system status.

        Checks validation first, then falls back to ``_last_connection_error``
        if available, and finally returns a generic message with remediation.
        """
        is_valid, error_message = await self._validate_system_status(tool_name)

        if not is_valid:
            return error_message

        tool_name = self._sanitize_tool_name(tool_name)
        base_msg = f"Unable to execute '{tool_name}' tool."

        if self._last_connection_error:
            return f"{base_msg}\n\n{self._last_connection_error}"

        return (
            f"{base_msg} Please ensure PiecesOS is running "
            "and try again. If the problem persists, run:\n\n"
            "`pieces restart`"
        )

    def _sanitize_tool_name(self, tool_name: str) -> str:
        """Sanitize tool name for safe inclusion in messages."""
        sanitized: str = re.sub(r"[^\w\s\-_.]", "", tool_name)
        return sanitized[:100]

    def _get_tools_hash(self, tools: list[types.Tool]) -> str | None:
        """Generate a stable SHA-256 hash of the tools list for change detection."""
        if not tools:
            return None

        hasher = hashlib.sha256()
        sorted_tools = sorted(tools, key=lambda t: t.name)

        for tool in sorted_tools:
            description = tool.description or ""
            truncated_desc = (
                description[:200] if len(description) > 200 else description
            )
            tool_sig = f"{tool.name}:{truncated_desc}"
            hasher.update(tool_sig.encode("utf-8"))

        return hasher.hexdigest()

    def _tools_have_changed(self, new_tools: list[types.Tool]) -> bool:
        """Check if the tools have changed since last check."""
        new_hash = self._get_tools_hash(new_tools)
        if self._previous_tools_hash is None:
            self._previous_tools_hash = new_hash
            return bool(new_tools)

        if new_hash != self._previous_tools_hash:
            Settings.logger.debug(
                f"Tools changed: old hash {self._previous_tools_hash}, new hash {new_hash}"
            )
            self._previous_tools_hash = new_hash
            return True
        return False

    async def update_tools(self, session: ClientSession, send_notification: bool = True) -> None:
        """Fetch tools from the session and handle change detection."""
        try:
            self.tools = await session.list_tools()
            new_discovered_tools = [
                tool[1] for tool in self.tools if tool[0] == "tools"
            ][0]

            tools_changed = self._tools_have_changed(new_discovered_tools)

            if tools_changed and self.discovered_tools:
                self.discovered_tools.clear()

            self.discovered_tools = new_discovered_tools

            Settings.logger.info(
                f"Discovered {len(self.discovered_tools)} tools from upstream server"
            )

            if send_notification and tools_changed:
                try:
                    Settings.logger.info("Tools have changed - sending notification")
                    await self._tools_changed_callback()
                except Exception as e:
                    Settings.logger.error(
                        f"Failed to notify IDE of tool changes: {e}. "
                        "Tools will be updated on the next request."
                    )

        except Exception as e:
            Settings.logger.error(f"Error fetching tools: {e}", exc_info=True)
            raise

    async def _connection_handler(self, send_notification: bool = True) -> None:
        """Handle the connection lifecycle in a single task context.

        Stages:
            1. Enter the streamable HTTP transport context manager and capture
               the upstream session ID for observability
            2. Create and enter a ``ClientSession`` with a public
               ``message_handler`` for notification handling
            3. Discover tools and set up notification handlers
            4. Wait for cleanup signal or cancellation
            5. Clean up resources in ``finally`` (orphaned + stale)

        Connection errors are stored in ``_last_connection_error`` so that
        the next ``call_tool`` can surface them to the user.
        """
        transport_ctx = None
        session_obj = None
        try:
            Settings.logger.info(
                f"Connecting to upstream MCP server at {self.upstream_url}"
            )

            transport_ctx = streamablehttp_client(self.upstream_url)
            read_stream, write_stream, get_session_id = await transport_ctx.__aenter__()
            self._transport_ctx = transport_ctx

            self._upstream_session_id = get_session_id()
            Settings.logger.debug(
                f"Transport session ID: {self._upstream_session_id or '(not yet assigned)'}"
            )

            session_obj = ClientSession(
                read_stream,
                write_stream,
                message_handler=self._make_message_handler(send_notification),
            )
            Settings.logger.info("Connecting to the client session")
            await session_obj.__aenter__()
            self.session = session_obj

            self._last_connection_error = None

            await self.update_tools(session_obj, send_notification)

            upstream_sid = get_session_id()
            if upstream_sid:
                self._upstream_session_id = upstream_sid

            Settings.logger.info(
                f"Connection established successfully "
                f"(session_id={self._upstream_session_id or 'N/A'})"
            )

            sentry_sdk.add_breadcrumb(
                message="MCP connection established",
                category="mcp",
                level="info",
                data={
                    "upstream_url": self.upstream_url,
                    "tools_count": len(self.discovered_tools),
                    "session_id": self._upstream_session_id,
                },
            )

            try:
                await self._cleanup_requested.wait()
                Settings.logger.debug("Cleanup requested, shutting down connection")
            except asyncio.CancelledError:
                Settings.logger.debug("Connection handler cancelled")
                raise

        except asyncio.CancelledError:
            Settings.logger.debug("Connection cancelled, cleaning up")
            raise
        except (
            httpx.ReadTimeout,
            httpx.ConnectTimeout,
            httpx.TimeoutException,
            httpcore.ReadTimeout,
            httpcore.ConnectTimeout,
        ) as e:
            self._last_connection_error = (
                f"Connection to PiecesOS timed out ({type(e).__name__}). "
                "This may happen if PiecesOS is overloaded or restarting. "
                "Try again, or run `pieces restart` if the issue persists."
            )
            Settings.logger.info(f"Connection timeout: {type(e).__name__}")
            sentry_sdk.add_breadcrumb(
                message="MCP connection timeout handled",
                category="mcp",
                level="info",
                data={
                    "timeout_type": type(e).__name__,
                    "upstream_url": self.upstream_url,
                },
            )
            return
        except (httpx.RemoteProtocolError, httpcore.RemoteProtocolError) as e:
            self._last_connection_error = (
                f"Connection to PiecesOS was interrupted ({type(e).__name__}). "
                "PiecesOS may have restarted. Retrying should reconnect automatically. "
                "If this persists, run `pieces restart`."
            )
            Settings.logger.info(
                f"Protocol error (connection interrupted): {type(e).__name__}"
            )
            sentry_sdk.add_breadcrumb(
                message="MCP protocol error handled",
                category="mcp",
                level="info",
                data={
                    "error_type": type(e).__name__,
                    "upstream_url": self.upstream_url,
                },
            )
            return
        except BrokenPipeError as e:
            self._last_connection_error = (
                "Connection to PiecesOS was lost (broken pipe). "
                "This usually means PiecesOS shut down unexpectedly. "
                "Run `pieces open` to restart it, then retry."
            )
            Settings.logger.info(
                "Stream resource broken (connection closed during send)"
            )
            sentry_sdk.add_breadcrumb(
                message="MCP stream resource broken handled",
                category="mcp",
                level="info",
                data={
                    "error_type": type(e).__name__,
                    "upstream_url": self.upstream_url,
                },
            )
            return
        except ValidationError as e:
            self._last_connection_error = (
                "PiecesOS sent a malformed response. This may indicate a version mismatch. "
                "Run `pieces update` to ensure you have the latest version, then `pieces restart`."
            )
            Settings.logger.info(
                "MCP server sent malformed JSON-RPC message (validation failed)"
            )
            sentry_sdk.add_breadcrumb(
                message="MCP JSON-RPC validation error handled",
                category="mcp",
                level="info",
                data={
                    "error_type": type(e).__name__,
                    "upstream_url": self.upstream_url,
                },
            )
            return
        except Exception as e:
            self._last_connection_error = (
                f"Unexpected connection error: {type(e).__name__}: {e}. "
                "Run `pieces restart` if this persists."
            )
            Settings.logger.error(f"Error in connection handler: {e}", exc_info=True)
            raise
        finally:
            if session_obj and self.session is None:
                try:
                    await session_obj.__aexit__(None, None, None)
                except Exception as cleanup_err:
                    Settings.logger.debug(f"Error cleaning up orphaned session: {cleanup_err}")
            if transport_ctx and self._transport_ctx is None:
                try:
                    await transport_ctx.__aexit__(None, None, None)
                except Exception as cleanup_err:
                    Settings.logger.debug(f"Error cleaning up orphaned transport: {cleanup_err}")
            await self._cleanup_stale_session()
            Settings.logger.debug("Connection handler cleanup completed")

    async def connect(self, send_notification: bool = True) -> ClientSession:
        """Ensure a connection to PiecesOS exists and return the session.

        Uses a polling loop to wait for ``_connection_handler`` to set
        ``self.session``.  The loop also checks for early task failure so
        that errors propagate immediately instead of waiting for the full
        10-second timeout.

        Returns:
            The active ``ClientSession``.

        Raises:
            ValueError: If the upstream URL cannot be resolved.
            TimeoutError: If the connection is not established within 10 s.
        """
        async with self.connection_lock:
            if self._event_loop is None:
                self._event_loop = asyncio.get_running_loop()

            session = self.session
            if (
                session is not None
                and self._connection_task
                and not self._connection_task.done()
            ):
                try:
                    await session.send_ping()
                    Settings.logger.debug("Using existing upstream connection")
                    return session
                except Exception as e:
                    Settings.logger.debug(
                        f"Existing connection is stale: {e}, creating new connection"
                    )

            await self._ensure_clean_state()

            if not self._try_get_upstream_url():
                raise ValueError(
                    "Cannot get MCP upstream URL - PiecesOS may not be running. "
                    "Run `pieces open` to start PiecesOS."
                )

            try:
                Settings.logger.info("Creating new connection to upstream server")

                self._cleanup_requested.clear()

                self._connection_task = asyncio.create_task(
                    self._connection_handler(send_notification)
                )

                Settings.logger.debug("Waiting for connection to establish...")
                for _attempt in range(self.CONNECTION_ESTABLISH_ATTEMPTS):
                    if self.session is not None:
                        Settings.logger.info("Connection established successfully")
                        return self.session
                    if self._connection_task.done():
                        exc = self._connection_task.exception()
                        if exc:
                            raise exc
                        break
                    await asyncio.sleep(self.CONNECTION_CHECK_INTERVAL)

                Settings.logger.error("Connection establishment timed out")
                if self._connection_task and not self._connection_task.done():
                    self._connection_task.cancel()
                    try:
                        await self._connection_task
                    except asyncio.CancelledError:
                        pass

                raise TimeoutError(
                    "Connection establishment timed out after 10 seconds. "
                    "PiecesOS may be starting up or overloaded. "
                    "Try again, or run `pieces restart`."
                )

            except Exception as e:
                await self._ensure_clean_state()
                Settings.logger.error(
                    f"Error connecting to upstream server: {e}", exc_info=True
                )
                raise

    async def _ensure_clean_state(self) -> None:
        """Ensure all connection state is properly cleaned up.

        Unlike ``_cleanup_stale_session`` (which cleans up within the
        connection handler's task context), this method is called from
        ``connect()`` and ``cleanup()`` to cancel the connection task
        and reset state from the outside.
        """
        Settings.logger.debug("Ensuring clean connection state")

        self._cleanup_requested.set()

        if self._connection_task and not self._connection_task.done():
            self._connection_task.cancel()
            try:
                await self._connection_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                Settings.logger.debug(f"Error cleaning up connection task: {e}")

        self.session = None
        self._transport_ctx = None
        self._connection_task = None

    def _make_message_handler(
        self, send_notification: bool = True
    ) -> Callable[[Any], Awaitable[None]]:
        """Create a ``message_handler`` callback for ``ClientSession``.

        Uses the SDK's public ``message_handler`` constructor parameter
        instead of monkey-patching the private ``_received_notification``
        attribute.  The handler is called *after* the SDK's built-in
        notification processing, so logging and other default behaviour
        is preserved.

        Only ``ToolListChangedNotification`` is handled here; all other
        message types (requests, exceptions) are ignored -- the SDK
        handles them internally.

        Args:
            send_notification: Forwarded to ``update_tools`` when a
                tool-list-changed notification arrives.

        Returns:
            An async callable suitable for the ``message_handler`` kwarg
            of ``ClientSession.__init__``.
        """
        conn = self

        async def _handler(message: Any) -> None:
            if not isinstance(message, types.ServerNotification):
                return
            Settings.logger.debug(f"Received notification: {message.root}")
            if isinstance(message.root, types.ToolListChangedNotification):
                session = conn.session
                if session is not None:
                    await conn.update_tools(session, send_notification=False)
                    await conn._tools_changed_callback()

        return _handler

    async def cleanup(self) -> None:
        """Clean up the upstream connection (full teardown)."""
        async with self.connection_lock:
            Settings.logger.info("Starting connection cleanup")

            await self._ensure_clean_state()

            self.discovered_tools = []

            Settings.logger.info("Connection cleanup completed")

    async def call_tool(self, name: str, arguments: dict) -> types.CallToolResult:
        """Call a tool on the PiecesOS MCP server.

        Performs 4-step validation, connects if needed, and forwards the
        call.  Errors are surfaced to the user with specific messages and
        remediation steps rather than being swallowed.
        """
        Settings.logger.debug(f"Calling tool: {name}")

        is_valid, error_message = await self._validate_system_status(name)
        if not is_valid:
            Settings.logger.debug(f"Tool validation failed for {name}: {error_message}")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=error_message)]
            )

        try:
            Settings.logger.debug(f"Calling upstream tool: {name}")
            session = await self.connect()

            result = await session.call_tool(name, arguments)
            Settings.logger.debug(f"Successfully called tool: {name}")
            Settings.logger.debug(f"with results: {result}")
            return result

        except TimeoutError:
            error_message = (
                f"Timed out connecting to PiecesOS while executing '{self._sanitize_tool_name(name)}'. "
                "PiecesOS may be starting up or overloaded. Please try again in a few seconds.\n\n"
                "If this persists, run: `pieces restart`"
            )
            Settings.logger.error(f"Timeout calling tool {name}")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=error_message)]
            )
        except (ConnectionError, OSError) as e:
            error_message = (
                f"Cannot reach PiecesOS to execute '{self._sanitize_tool_name(name)}'. "
                "Please ensure PiecesOS is running with `pieces open`, then retry.\n\n"
                f"Error: {e}"
            )
            Settings.logger.error(f"Connection error calling tool {name}: {e}")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=error_message)]
            )
        except Exception as e:
            Settings.logger.error(f"Error calling POS MCP {name}: {e}", exc_info=True)

            error_message = await self._get_error_message_for_tool(name)
            error_message += f"\n\nError details: {type(e).__name__}: {e}"
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=error_message)]
            )


class MCPGateway:
    """Gateway server between IDE clients (stdio) and PiecesOS (upstream).

    Routes ``list_tools`` and ``call_tool`` requests from the IDE to PiecesOS,
    handles tool change notifications, and manages the upstream connection
    lifecycle.
    """

    def __init__(self, server_name: str, upstream_url: str | None):
        self.server_name: str = server_name
        self.server = Server(server_name)
        self.upstream = PosMcpConnection(
            upstream_url, self.send_tools_changed_notification
        )

        sentry_sdk.set_context(
            "mcp_gateway",
            {
                "server_name": server_name,
                "upstream_url": upstream_url,
                "connection_type": "stdio",
            },
        )
        sentry_sdk.set_tag("mcp_server", server_name)

        self.setup_handlers()

    async def send_tools_changed_notification(self) -> None:
        """Send a tools/list_changed notification to the IDE client."""
        try:
            ctx = self.server.request_context
            await ctx.session.send_notification(
                notification=types.ServerNotification(
                    root=types.ToolListChangedNotification(
                        method="notifications/tools/list_changed"
                    )
                )
            )
            Settings.logger.info("Sent tools/list_changed notification to client")
        except LookupError:
            Settings.logger.info("No active request context — can't send notification.")
        except Exception as e:
            Settings.logger.error(f"Failed to send tools changed notification: {e}")
            Settings.logger.info(
                "Tools have changed - clients will receive updated tools on next request"
            )

    def setup_handlers(self) -> None:
        """Set up the request handlers for the gateway server."""
        Settings.logger.info("Setting up gateway request handlers")

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            Settings.logger.debug("Received list_tools request")

            if await self.upstream._check_pieces_os_status():
                await self.upstream.connect(send_notification=False)

                Settings.logger.debug(
                    f"Successfully connected - returning {len(self.upstream.discovered_tools)} live tools"
                )
                return self.upstream.discovered_tools
            else:
                if self.upstream.discovered_tools:
                    Settings.logger.warning(
                        "PiecesOS is not running -- returning previously cached tools. "
                        "Results may be stale. Run `pieces open` to reconnect."
                    )
                    return self.upstream.discovered_tools

                Settings.logger.warning(
                    "PiecesOS is not running and no cached tools available -- "
                    "returning fallback tool definitions. Run `pieces open` to start PiecesOS."
                )
                return PIECES_MCP_TOOLS_CACHE

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[types.ContentBlock]:
            Settings.logger.debug(
                f"Received call_tool request for {name}, With args {arguments}"
            )
            pos_returnable = await self.upstream.call_tool(name, arguments)
            Settings.logger.debug(f"POS returnable {pos_returnable}")
            return pos_returnable.content

    async def run(self) -> None:
        """Run the gateway server (stdio transport)."""
        try:
            Settings.logger.info("Starting MCP Gateway server")

            sentry_sdk.add_breadcrumb(
                message="MCP Gateway starting",
                category="mcp",
                level="info",
                data={
                    "server_name": self.server_name,
                    "upstream_url": self.upstream.upstream_url,
                },
            )
            if self.upstream.upstream_url:
                try:
                    await self.upstream.connect(send_notification=False)
                except Exception as e:
                    Settings.logger.warning(
                        f"Could not connect to PiecesOS at startup: {e}. "
                        "The gateway will continue and retry on the next tool call. "
                        "Ensure PiecesOS is running with `pieces open`."
                    )

            Settings.logger.info(f"Starting stdio server for {self.server.name}")
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.server.name,
                        server_version="0.2.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(
                                tools_changed=True
                            ),
                            experimental_capabilities={},
                        ),
                    ),
                )
        except KeyboardInterrupt:
            Settings.logger.info("Gateway interrupted by user")
        except Exception as e:
            if (
                "BrokenResourceError" in str(e)
                or "unhandled errors in a TaskGroup" in str(e)
                or ("ValidationError" in str(type(e)) and "JSONRPCMessage" in str(e))
            ):
                Settings.logger.debug(f"Gateway server shutdown cleanly: {e}")
            else:
                Settings.logger.error(
                    f"Error running gateway server: {e}", exc_info=True
                )
        finally:
            Settings.logger.info("Gateway shutting down, cleaning up connections")
            try:
                await self.upstream.cleanup()
            except Exception as e:
                Settings.logger.debug(f"Error during cleanup: {e}")


async def _run_with_shutdown(gateway: MCPGateway, shutdown_event: asyncio.Event) -> None:
    """Run the gateway and cancel it when the shutdown event is set.

    This wires up the signal-handler-set ``shutdown_event`` so that
    SIGTERM/SIGINT actually trigger a graceful shutdown.
    """
    gateway_task = asyncio.create_task(gateway.run())
    shutdown_task = asyncio.create_task(shutdown_event.wait())
    done, pending = await asyncio.wait(
        [gateway_task, shutdown_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


async def main() -> None:
    """Entry point for the MCP gateway process.

    Startup sequence:
        1. Set up the asyncio exception handler
        2. Register signal handlers for graceful shutdown
        3. Create WebSocket instances (Health, Auth, LTM Vision)
        4. Resolve the upstream MCP URL
        5. Create and run the gateway
        6. On shutdown, close WebSockets and clean up
    """
    Settings.logger.info("Starting MCP Gateway")
    is_pos_stream_running_lock = threading.Lock()
    upstream_connection = None

    def asyncio_exception_handler(loop: asyncio.AbstractEventLoop, context: dict) -> None:
        exc = context.get("exception")

        if isinstance(exc, (httpx.RemoteProtocolError)):
            with is_pos_stream_running_lock:
                Settings.pieces_client.is_pos_stream_running = False

            Settings.logger.info(
                f"POS stream stopped due to HTTP timeout/connection error: {type(exc).__name__}"
            )

            if upstream_connection:
                upstream_connection.request_cleanup()
        elif isinstance(
            exc,
            (
                httpx.ReadTimeout,
                httpx.ConnectTimeout,
                httpx.TimeoutException,
                httpcore.ReadTimeout,
                httpcore.ConnectTimeout,
            ),
        ):
            Settings.logger.info(
                f"Timeout error (handled gracefully): {type(exc).__name__}"
            )
            sentry_sdk.add_breadcrumb(
                message="MCP timeout handled by async exception handler",
                category="mcp",
                level="info",
                data={"timeout_type": type(exc).__name__},
            )
        elif "BrokenResourceError" in str(type(exc)) or "BrokenResourceError" in str(
            exc
        ):
            Settings.logger.info(
                "Stream resource broken in async handler (connection closed during send)"
            )
            sentry_sdk.add_breadcrumb(
                message="Stream resource broken handled by async exception handler",
                category="mcp",
                level="info",
                data={
                    "error_type": type(exc).__name__ if exc else "BrokenResourceError"
                },
            )
        elif exc and (
            "ValidationError" in str(type(exc)) and "JSONRPCMessage" in str(exc)
        ):
            Settings.logger.info(
                "MCP JSON-RPC validation error in async handler (server sent malformed message)"
            )
            sentry_sdk.add_breadcrumb(
                message="MCP JSON-RPC validation error handled by async exception handler",
                category="mcp",
                level="info",
                data={
                    "error_type": type(exc).__name__,
                    "error_message": str(exc)[:200] if exc else "ValidationError",
                },
            )
        else:
            Settings.logger.error(
                f"Unexpected async error: {context}. "
                "If this causes issues, try `pieces restart`."
            )
            if exc:
                sentry_sdk.capture_exception(exc)

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(asyncio_exception_handler)

    shutdown_event = asyncio.Event()

    def signal_handler() -> None:
        Settings.logger.info("Received shutdown signal")
        shutdown_event.set()

    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
    if hasattr(signal, "SIGINT"):
        signal.signal(signal.SIGINT, lambda s, f: signal_handler())

    ltm_vision = LTMVisionWS(Settings.pieces_client, lambda x: None)
    user_ws = AuthWS(
        Settings.pieces_client, lambda x: None, lambda x: ltm_vision.start()
    )

    def on_ws_event(ws: Any, e: Exception) -> None:
        if isinstance(e, WebSocketConnectionClosedException):
            with is_pos_stream_running_lock:
                Settings.pieces_client.is_pos_stream_running = False
            if upstream_connection:
                upstream_connection.request_cleanup()
        else:
            Settings.logger.error(f"Health WS error: {e}")

    health_ws = HealthWS(
        Settings.pieces_client,
        lambda x: None,
        lambda ws: user_ws.start(),
        on_error=on_ws_event,
    )

    upstream_url = None
    if Settings.pieces_client.is_pieces_running():
        upstream_url = get_mcp_latest_url()
        sentry_sdk.set_user({"id": Settings.get_os_id() or "unknown"})
        health_ws.start()

    gateway = MCPGateway(
        server_name="pieces-stdio-mcp",
        upstream_url=upstream_url,
    )

    upstream_connection = gateway.upstream

    try:
        await _run_with_shutdown(gateway, shutdown_event)
    except KeyboardInterrupt:
        Settings.logger.info("Gateway interrupted by user")
    except Exception as e:
        Settings.logger.error(f"Unexpected error in main: {e}", exc_info=True)
    finally:
        Settings.logger.info("MCP Gateway shutting down")

        async def _close_ws(ws_instance: Any) -> None:
            try:
                await asyncio.wait_for(
                    asyncio.to_thread(ws_instance.close), timeout=5.0
                )
            except Exception:
                pass

        await asyncio.gather(
            *(_close_ws(ws) for ws in [ltm_vision, user_ws, health_ws]),
            return_exceptions=True,
        )
