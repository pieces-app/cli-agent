import asyncio
import hashlib
from pydantic import ValidationError
import sentry_sdk
import signal
import threading
from typing import Tuple, Callable, Awaitable
import httpx
import httpcore

from websocket import WebSocketConnectionClosedException
from pieces.mcp.utils import get_mcp_latest_url
from pieces.mcp.tools_cache import PIECES_MCP_TOOLS_CACHE
from pieces.settings import Settings
from .._vendor.pieces_os_client.wrapper.version_compatibility import (
    UpdateEnum,
    VersionChecker,
)
from .._vendor.pieces_os_client.wrapper.websockets.health_ws import HealthWS
from .._vendor.pieces_os_client.wrapper.websockets.ltm_vision_ws import LTMVisionWS
from .._vendor.pieces_os_client.wrapper.websockets.auth_ws import AuthWS
from mcp.client.sse import sse_client
from mcp import ClientSession
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions


class PosMcpConnection:
    """Manages connection to the Pieces MCP server."""

    def __init__(
        self, upstream_url: str, tools_changed_callback: Callable[[], Awaitable[None]]
    ):
        self.upstream_url = (
            upstream_url  # Can be None if PiecesOS wasn't running at startup
        )
        self.CONNECTION_ESTABLISH_ATTEMPTS = 100
        self.CONNECTION_CHECK_INTERVAL = 0.1
        self.session = None
        self.sse_client = None
        self.discovered_tools = []
        self.connection_lock = asyncio.Lock()
        self._pieces_os_running = None
        self._ltm_enabled = None
        self.result = None
        self._previous_tools_hash = None
        self._tools_changed_callback = tools_changed_callback
        self._health_check_lock = threading.Lock()

        # Add cleanup coordination
        self._cleanup_requested = asyncio.Event()
        self._connection_task = None

    def _try_get_upstream_url(self):
        """Try to get the upstream URL if we don't have it yet."""
        if self.upstream_url is None:
            if Settings.pieces_client.is_pieces_running():
                try:
                    self.upstream_url = get_mcp_latest_url()
                    return True
                except:  # noqa: E722
                    pass
            return False
        return True

    def request_cleanup(self):
        """Request cleanup from exception handler (thread-safe)."""
        Settings.logger.debug("Cleanup requested from exception handler")

        # Use asyncio's thread-safe method to schedule cleanup
        loop = None
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            Settings.logger.debug("No running loop for cleanup request")
            return

        if loop and not loop.is_closed():
            # Schedule cleanup in the event loop
            loop.call_soon_threadsafe(self._schedule_cleanup)

    def _schedule_cleanup(self):
        """Internal method to schedule cleanup in the event loop."""
        # Set cleanup event
        self._cleanup_requested.set()

        # Cancel connection task if it exists
        if self._connection_task and not self._connection_task.done():
            self._connection_task.cancel()
            Settings.logger.debug("Connection task cancelled due to cleanup request")

    async def _cleanup_stale_session(self):
        """Clean up a stale session and its resources."""
        # Store references to avoid race conditions
        session = self.session
        sse_client = self.sse_client

        # Clear instance variables immediately
        self.session = None
        self.sse_client = None
        self.discovered_tools = []

        # Clean up session if it exists
        if session:
            try:
                await session.__aexit__(None, None, None)
                Settings.logger.debug("Session cleaned up successfully")
            except Exception as e:
                Settings.logger.debug(f"Error cleaning up session: {e}")

        # Clean up SSE client if it exists
        if sse_client:
            try:
                await sse_client.__aexit__(None, None, None)
                Settings.logger.debug("SSE client cleaned up successfully")
            except Exception as e:
                Settings.logger.debug(f"Error cleaning up SSE client: {e}")

    def _check_version_compatibility(self) -> Tuple[bool, str]:
        """
        Check if the PiecesOS version is compatible with the MCP server.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating compatibility, str: message if it is not compatible.
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

        # These messages are sent to the llm to update the respective tool
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

    def _check_pieces_os_status(self):
        """Check if PiecesOS is running using health WebSocket"""
        with self._health_check_lock:
            # First check if already connected
            if HealthWS.is_running() and Settings.pieces_client.is_pos_stream_running:
                return True

            # Check if PiecesOS is available
            if not Settings.pieces_client.is_pieces_running(2):
                return False

            try:
                health_ws = HealthWS.get_instance()
                if health_ws:
                    health_ws.start()

                sentry_sdk.set_user({"id": Settings.get_os_id() or "unknown"})

                # Update the user profile cache
                Settings.pieces_client.user.user_profile = (
                    Settings.pieces_client.user_api.user_snapshot().user
                )

                # Update LTM status cache
                Settings.pieces_client.copilot.context.ltm.ltm_status = Settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status()
                return True
            except Exception as e:
                Settings.logger.debug(f"Failed to start health WebSocket: {e}")
                return False

    def _check_ltm_status(self):
        """Check if LTM is enabled."""
        return Settings.pieces_client.copilot.context.ltm.is_enabled

    def _validate_system_status(self, tool_name: str) -> tuple[bool, str]:
        """
        Perform 4-step validation before executing any command:
        1. Check health WebSocket
        2. Check compatibility
        3. Check Auth
        4. Check LTM (for LTM tools)

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Step 1: Check health WebSocket / PiecesOS status
        if not self._check_pieces_os_status():
            return False, (
                "PiecesOS is not running. To use this tool, please run:\n\n"
                "`pieces open`\n\n"
                "This will start PiecesOS, then you can retry your request."
            )

        # Step 2: Check version compatibility
        is_compatible, compatibility_message = self._check_version_compatibility()
        if not is_compatible:
            return False, compatibility_message

        # Step 3: Check Auth status
        if not Settings.pieces_client.user.user_profile:
            return False, (
                "User must sign up to use this tool, please run:\n\n`pieces login`\n\n"
                "This will open the authentication page in your browser. After signing in, you can retry your request."
            )

        # Step 4: Check LTM status (only for LTM-related tools)
        if tool_name in ["ask_pieces_ltm", "create_pieces_memory"]:
            ltm_enabled = self._check_ltm_status()
            if not ltm_enabled:
                return False, (
                    "PiecesOS is running but Long Term Memory (LTM) is not enabled. "
                    "To use this tool, please run:\n\n"
                    "`pieces open --ltm`\n\n"
                    "This will enable LTM, then you can retry your request."
                )

        # All checks passed
        return True, ""

    def _get_error_message_for_tool(self, tool_name: str) -> str:
        """Get appropriate error message based on the tool and system status."""
        # Use the 3-step validation system
        is_valid, error_message = self._validate_system_status(tool_name)

        if not is_valid:
            return error_message
        tool_name = self._sanitize_tool_name(tool_name)
        # If all validations pass but we still have an error, return generic message

        return (
            f"Unable to execute '{tool_name}' tool. Please ensure PiecesOS is running "
            "and try again. If the problem persists, run:\n\n"
            "`pieces restart`"
        )

    def _sanitize_tool_name(self, tool_name: str) -> str:
        """Sanitize tool name for safe inclusion in messages."""
        import re

        # Remove control characters and limit length
        sanitized = re.sub(r"[^\w\s\-_.]", "", tool_name)
        return sanitized[:100]  # Limit to reasonable length

    def _get_tools_hash(self, tools):
        """Generate a hash of the tools list for change detection."""
        if not tools:
            return None

        # Create a stable hash using SHA256
        hasher = hashlib.sha256()

        # Sort tools by name for consistency
        sorted_tools = sorted(tools, key=lambda t: t.name)

        for tool in sorted_tools:
            # Use truncated description to catch content changes while avoiding memory issues
            description = tool.description or ""
            truncated_desc = (
                description[:200] if len(description) > 200 else description
            )
            tool_sig = f"{tool.name}:{truncated_desc}"
            hasher.update(tool_sig.encode("utf-8"))

        return hasher.hexdigest()

    def _tools_have_changed(self, new_tools):
        """Check if the tools have changed since last check."""
        new_hash = self._get_tools_hash(new_tools)
        if self._previous_tools_hash is None:
            # First time, consider as changed if we have tools
            self._previous_tools_hash = new_hash
            return bool(new_tools)

        if new_hash != self._previous_tools_hash:
            Settings.logger.debug(
                f"Tools changed: old hash {self._previous_tools_hash}, new hash {new_hash}"
            )
            self._previous_tools_hash = new_hash
            return True
        return False

    async def update_tools(self, session, send_notification: bool = True):
        """Fetch tools from the session and handle change detection."""
        try:
            self.tools = await session.list_tools()
            new_discovered_tools = [
                tool[1] for tool in self.tools if tool[0] == "tools"
            ][0]

            # Check if tools have changed
            tools_changed = self._tools_have_changed(new_discovered_tools)

            # Clean up old tool data if changed
            if tools_changed and self.discovered_tools:
                # Clear references to old tools to prevent memory buildup
                self.discovered_tools.clear()

            self.discovered_tools = new_discovered_tools

            Settings.logger.info(
                f"Discovered {len(self.discovered_tools)} tools from upstream server"
            )

            # If tools changed, call the callback
            if send_notification and tools_changed:
                try:
                    Settings.logger.info("Tools have changed - sending notification")
                    await self._tools_changed_callback()
                except Exception as e:
                    Settings.logger.error(f"Error in tools changed callback: {e}")

        except Exception as e:
            Settings.logger.error(f"Error fetching tools: {e}", exc_info=True)
            raise

    async def _connection_handler(self, send_notification: bool = True):
        """Handle the connection lifecycle in a single task context."""
        try:
            Settings.logger.info(
                f"Connecting to upstream MCP server at {self.upstream_url}"
            )

            # Enter SSE client context
            self.sse_client = sse_client(self.upstream_url)
            read_stream, write_stream = await self.sse_client.__aenter__()

            # Enter session context
            session = ClientSession(read_stream, write_stream)
            Settings.logger.info("Connecting to the client session")
            await session.__aenter__()
            self.session = session

            # Update tools and setup notifications
            await self.update_tools(session, send_notification)
            await self.setup_notification_handler(session)

            Settings.logger.info("Connection established successfully")

            # Add Sentry breadcrumb for successful MCP connection
            sentry_sdk.add_breadcrumb(
                message="MCP connection established",
                category="mcp",
                level="info",
                data={
                    "upstream_url": self.upstream_url,
                    "tools_count": len(self.discovered_tools),
                },
            )

            # Keep connection alive until cleanup is requested or cancelled
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
            # Handle SSE timeout errors gracefully without sending to Sentry
            Settings.logger.info(
                f"SSE connection timeout (expected for long-running connections): {type(e).__name__}"
            )
            sentry_sdk.add_breadcrumb(
                message="SSE connection timeout handled",
                category="mcp",
                level="info",
                data={
                    "timeout_type": type(e).__name__,
                    "upstream_url": self.upstream_url,
                },
            )
            # Don't re-raise - this is a normal part of SSE connection lifecycle
            return
        except (httpx.RemoteProtocolError, httpcore.RemoteProtocolError) as e:
            # Handle protocol errors gracefully
            Settings.logger.info(
                f"SSE protocol error (connection interrupted): {type(e).__name__}"
            )
            sentry_sdk.add_breadcrumb(
                message="SSE protocol error handled",
                category="mcp",
                level="info",
                data={
                    "error_type": type(e).__name__,
                    "upstream_url": self.upstream_url,
                },
            )
            # Don't re-raise - this is expected when connections are interrupted
            return
        except BrokenPipeError as e:
            Settings.logger.info(
                "SSE stream resource broken (connection closed during send)"
            )
            sentry_sdk.add_breadcrumb(
                message="SSE stream resource broken handled",
                category="mcp",
                level="info",
                data={
                    "error_type": type(e).__name__,
                    "upstream_url": self.upstream_url,
                },
            )
            return
        except ValidationError as e:
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
            Settings.logger.error(f"Error in connection handler: {e}", exc_info=True)
            raise
        finally:
            # Cleanup happens in the same task context where __aenter__ was called
            await self._cleanup_stale_session()
            Settings.logger.debug("Connection handler cleanup completed")

    async def connect(self, send_notification: bool = True):
        """Ensures a connection to the POS server exists and returns it."""
        async with self.connection_lock:
            # Check if we have a valid existing connection
            if (
                self.session is not None
                and self._connection_task
                and not self._connection_task.done()
            ):
                try:
                    await self.session.send_ping()
                    Settings.logger.debug("Using existing upstream connection")
                    return self.session
                except Exception as e:
                    Settings.logger.debug(
                        f"Existing connection is stale: {e}, creating new connection"
                    )
                    # Fall through to create new connection

            # Clean up any existing connection state
            await self._ensure_clean_state()

            # Try to get upstream URL if we don't have it
            if not self._try_get_upstream_url():
                raise ValueError(
                    "Cannot get MCP upstream URL - PiecesOS may not be running"
                )

            try:
                Settings.logger.info("Creating new connection to upstream server")

                # Reset cleanup event for new connection
                self._cleanup_requested.clear()

                # Start connection in a dedicated task
                self._connection_task = asyncio.create_task(
                    self._connection_handler(send_notification)
                )

                # Wait for connection to establish with longer timeout
                Settings.logger.debug("Waiting for connection to establish...")
                for attempt in range(
                    self.CONNECTION_ESTABLISH_ATTEMPTS
                ):  # Wait up to 10 seconds
                    if self.session is not None:
                        Settings.logger.info("Connection established successfully")
                        return self.session
                    await asyncio.sleep(self.CONNECTION_CHECK_INTERVAL)

                # Timeout occurred - clean up the running task
                Settings.logger.error("Connection establishment timed out")
                if self._connection_task and not self._connection_task.done():
                    self._connection_task.cancel()
                    try:
                        await self._connection_task
                    except asyncio.CancelledError:
                        pass

                raise TimeoutError(
                    "Connection establishment timed out after 10 seconds"
                )

            except Exception as e:
                # Ensure clean state on any error
                await self._ensure_clean_state()
                Settings.logger.error(
                    f"Error connecting to upstream server: {e}", exc_info=True
                )
                raise

    async def _ensure_clean_state(self):
        """Ensure all connection state is properly cleaned up."""
        Settings.logger.debug("Ensuring clean connection state")

        # Signal cleanup if needed
        self._cleanup_requested.set()

        # Cancel and wait for existing connection task
        if self._connection_task and not self._connection_task.done():
            self._connection_task.cancel()
            try:
                await self._connection_task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                Settings.logger.debug(f"Error cleaning up connection task: {e}")

        # Reset all state
        self.session = None
        self.sse_client = None
        self._connection_task = None
        # Note: Don't clear discovered_tools here - keep them for fallback

    async def setup_notification_handler(self, session):
        """Setup the notification handler for the session."""
        if not hasattr(self, "main_notification_handler"):
            self.main_notification_handler = session._received_notification

        async def received_notification_handler(
            notification: types.ServerNotification,
        ):
            """Handle received notifications from the SSE client."""
            Settings.logger.debug(f"Received notification: {notification.root}")
            if isinstance(notification.root, types.ToolListChangedNotification):
                await self.update_tools(session, send_notification=False)
                await self._tools_changed_callback()
            await self.main_notification_handler(notification)

        session._received_notification = received_notification_handler

    async def cleanup(self):
        """Cleans up the upstream connection."""
        async with self.connection_lock:
            Settings.logger.info("Starting connection cleanup")

            # Ensure clean state (this handles task cancellation and cleanup)
            await self._ensure_clean_state()

            # Clear discovered tools on full cleanup
            self.discovered_tools = []

            Settings.logger.info("Connection cleanup completed")

    async def call_tool(self, name, arguments):
        """Calls a tool on the POS MCP server."""
        Settings.logger.debug(f"Calling tool: {name}")

        # Perform 3-step validation before attempting to call tool
        is_valid, error_message = self._validate_system_status(name)
        if not is_valid:
            Settings.logger.debug(f"Tool validation failed for {name}: {error_message}")
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=error_message)]
            )

        # All validations passed, try to call the upstream tool
        try:
            Settings.logger.debug(f"Calling upstream tool: {name}")
            session = await self.connect()

            result = await session.call_tool(name, arguments)
            Settings.logger.debug(f"Successfully called tool: {name}")
            Settings.logger.debug(f"with results: {result}")
            return result

        except Exception as e:
            Settings.logger.error(f"Error calling POS MCP {name}: {e}", exc_info=True)

            # Return a helpful error message based on the tool and system status
            error_message = self._get_error_message_for_tool(name)
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=error_message)]
            )


class MCPGateway:
    """Gateway server between POS MCP server and stdio."""

    def __init__(self, server_name, upstream_url):
        self.server_name = server_name
        self.server = Server(server_name)
        self.upstream = PosMcpConnection(
            upstream_url, self.send_tools_changed_notification
        )

        # Add MCP server info to Sentry context
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

    async def send_tools_changed_notification(self):
        """Send a tools/list_changed notification to the client."""
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

    def setup_handlers(self):
        """Sets up the request handlers for the gateway server."""
        Settings.logger.info("Setting up gateway request handlers")

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            Settings.logger.debug("Received list_tools request")

            if self.upstream._check_pieces_os_status():
                await self.upstream.connect(send_notification=False)

                Settings.logger.debug(
                    f"Successfully connected - returning {len(self.upstream.discovered_tools)} live tools"
                )
                return self.upstream.discovered_tools
            else:
                # Only use cached/fallback tools when PiecesOS is not running
                if self.upstream.discovered_tools:
                    Settings.logger.debug(
                        f"PiecesOS not running - returning cached tools: {len(self.upstream.discovered_tools)} tools"
                    )
                    return self.upstream.discovered_tools

                Settings.logger.debug("PiecesOS not running - returning fallback tools")
                # Use the hardcoded fallback tools
                Settings.logger.debug(
                    f"Returning {len(PIECES_MCP_TOOLS_CACHE)} fallback tools"
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

    async def run(self):
        """Runs the gateway server."""
        try:
            Settings.logger.info("Starting MCP Gateway server")

            # Add Sentry breadcrumb for MCP gateway startup
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
                    Settings.logger.error(f"Failed to connect to upstream server {e}")

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
            # Handle specific MCP-related errors more gracefully
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
            # Ensure we clean up the connection when the gateway exits
            # But do it in a way that doesn't interfere with stdio cleanup
            Settings.logger.info("Gateway shutting down, cleaning up connections")
            try:
                await self.upstream.cleanup()
            except Exception as e:
                Settings.logger.debug(f"Error during cleanup: {e}")


async def main():
    # Just initialize settings without starting services
    Settings.logger.info("Starting MCP Gateway")
    is_pos_stream_running_lock = threading.Lock()
    upstream_connection = None

    def asyncio_exception_handler(loop, context):
        exc = context.get("exception")

        # Handle HTTP timeout and connection-related errors without sending to Sentry
        if isinstance(exc, (httpx.RemoteProtocolError)):
            with is_pos_stream_running_lock:
                Settings.pieces_client.is_pos_stream_running = False

            # Log at info level instead of debug for better visibility
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
            # Add breadcrumb but don't send exception to Sentry
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
                "SSE stream resource broken in async handler (connection closed during send)"
            )
            # Add breadcrumb but don't send exception to Sentry
            sentry_sdk.add_breadcrumb(
                message="SSE stream resource broken handled by async exception handler",
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
            # Add breadcrumb but don't send exception to Sentry
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
            Settings.logger.error(f"Async exception: {context}")

    loop = asyncio.get_event_loop()
    loop.set_exception_handler(asyncio_exception_handler)

    # Set up signal handlers for graceful shutdown
    shutdown_event = asyncio.Event()

    def signal_handler():
        Settings.logger.info("Received shutdown signal")
        shutdown_event.set()

    # Register signal handlers
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, lambda s, f: signal_handler())
    if hasattr(signal, "SIGINT"):
        signal.signal(signal.SIGINT, lambda s, f: signal_handler())

    # HealthWS starts the AuthWS, which starts the LTMVisionWS
    ltm_vision = LTMVisionWS(Settings.pieces_client, lambda x: None)
    user_ws = AuthWS(
        Settings.pieces_client, lambda x: None, lambda x: ltm_vision.start()
    )

    def on_ws_event(ws, e):
        if isinstance(e, WebSocketConnectionClosedException):
            with is_pos_stream_running_lock:
                Settings.pieces_client.is_pos_stream_running = False
            # Also request cleanup if we have the connection reference
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

    # Try to get the MCP URL, but continue even if it fails
    upstream_url = None
    if Settings.pieces_client.is_pieces_running():
        upstream_url = get_mcp_latest_url()
        sentry_sdk.set_user({"id": Settings.get_os_id() or "unknown"})
        health_ws.start()

    gateway = MCPGateway(
        server_name="pieces-stdio-mcp",
        upstream_url=upstream_url,
    )

    # Store reference for exception handler
    upstream_connection = gateway.upstream

    try:
        await gateway.run()
    except KeyboardInterrupt:
        Settings.logger.info("Gateway interrupted by user")
    except Exception as e:
        Settings.logger.error(f"Unexpected error in main: {e}", exc_info=True)
    finally:
        Settings.logger.info("MCP Gateway shutting down")
