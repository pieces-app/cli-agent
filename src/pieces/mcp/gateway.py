import asyncio
from typing import Tuple
from pieces.mcp.utils import get_mcp_latest_url
from pieces.mcp.tools_cache import get_available_tools, MCPToolsCache, PIECES_MCP_TOOLS_CACHE
from pieces.settings import Settings
from .._vendor.pieces_os_client.wrapper.version_compatibility import (
    UpdateEnum,
    VersionChecker,
)
from .._vendor.pieces_os_client.wrapper.websockets.health_ws import HealthWS
from .._vendor.pieces_os_client.wrapper.websockets.ltm_vision_ws import LTMVisionWS
from mcp.client.sse import sse_client
from mcp import ClientSession
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions
from mcp.server.models import InitializationOptions


class PosMcpConnection:
    """Manages connection to the Pieces MCP server."""

    def __init__(self, upstream_url):
        self.upstream_url = (
            upstream_url  # Can be None if PiecesOS wasn't running at startup
        )
        self.session = None
        self.sse_client = None
        self.discovered_tools = []
        self.connection_lock = asyncio.Lock()
        self._pieces_os_running = None
        self._ltm_enabled = None
        self.cache_manager = MCPToolsCache()
        self.result = None

    def _try_get_upstream_url(self):
        """Try to get the upstream URL if we don't have it yet."""
        if self.upstream_url is None:
            if Settings.pieces_client.is_pieces_running():
                self.upstream_url = get_mcp_latest_url()
                return True
            return False
        return True

    async def _cleanup_stale_session(self):
        """Clean up a stale session and its resources."""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
        except Exception as e:
            Settings.logger.debug(f"Error cleaning up stale session: {e}")

        try:
            if self.sse_client:
                await self.sse_client.__aexit__(None, None, None)
        except Exception as e:
            Settings.logger.debug(f"Error cleaning up stale SSE client: {e}")

        # Reset connection state
        self.discovered_tools = []

    def _check_version_compatibility(self) -> Tuple[bool, str]:
        """
        Check if the PiecesOS version is compatible with the MCP server.

        Returns:
            Tuple[bool, str]: A tuple containing a boolean indicating compatibility, str: message if it is not compatible.
        """
        if not self.result:
            self.result = VersionChecker(
                Settings.PIECES_OS_MIN_VERSION,
                Settings.PIECES_OS_MAX_VERSION,
                Settings.pieces_client.version,
            ).version_check()

        if self.result.compatible:
            return True, ""

        # These messages are sent to the llm to update the respective tool
        if self.result.update == UpdateEnum.Plugin:
            return (
                False,
                "Please update the CLI version to be able to run the tool call, run 'pieces manage update' to get the latest version. then retry your request again after updating.",
            )
        else:
            return (
                False,
                "Please update PiecesOS to a compatible version to be able to run the tool call. run 'pieces update' to get the latest version. then retry your request again after updating.",
            )

    def _check_pieces_os_status(self):
        """Check if PiecesOS is running using health WebSocket"""
        # First check if health_ws is already running and connected
        if HealthWS.is_running() and getattr(
            Settings.pieces_client, "is_pos_stream_running", False
        ):
            return True

        # If health_ws is not running, check if PiecesOS is available
        if Settings.pieces_client.is_pieces_running():
            try:
                # Try to start the health WebSocket
                if health_ws := Settings.pieces_client.health_ws:
                    health_ws.start()
                else:
                    # This should not happen as we initialized health_ws in main
                    Settings.show_error(
                        "Unexpected error healthWS is not inilitialized"
                    )
                ## Update the ltm status cache
                Settings.pieces_client.copilot.context.ltm.ltm_status = Settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status()
                return True
            except Exception as e:
                Settings.logger.debug(f"Failed to start health WebSocket: {e}")
                return False

        return False

    def _check_ltm_status(self):
        """Check if LTM is enabled."""
        return Settings.pieces_client.copilot.context.ltm.is_enabled

    def _validate_system_status(self, tool_name: str) -> tuple[bool, str]:
        """
        Perform 3-step validation before executing any command:
        1. Check health WebSocket
        2. Check compatibility
        3. Check LTM (for LTM tools)

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        # Step 1: Check health WebSocket / PiecesOS status
        if not self._check_pieces_os_status():
            return False, (
                f"PiecesOS is not running. To use the '{tool_name}' tool, please run:\n\n"
                "`pieces open`\n\n"
                "This will start PiecesOS, then you can retry your request."
            )

        # Step 2: Check version compatibility
        is_compatible, compatibility_message = self._check_version_compatibility()
        if not is_compatible:
            return False, compatibility_message

        # Step 3: Check LTM status (only for LTM-related tools)
        if tool_name in ["ask_pieces_ltm", "create_pieces_memory"]:
            ltm_enabled = self._check_ltm_status()
            if not ltm_enabled:
                return False, (
                    f"PiecesOS is running but Long Term Memory (LTM) is not enabled. "
                    f"To use the '{tool_name}' tool, please run:\n\n"
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

        # If all validations pass but we still have an error, return generic message
        return (
            f"Unable to execute '{tool_name}' tool. Please ensure PiecesOS is running "
            "and try again. If the problem persists, run:\n\n"
            "`pieces restart`"
        )

    async def connect(self):
        """Ensures a connection to the POS server exists and returns it."""
        async with self.connection_lock:
            if self.session is not None:
                # Validate the existing session is still alive
                try:
                    await self.session.send_ping()
                    Settings.logger.debug("Using existing upstream connection")
                    return self.session
                except Exception as e:
                    Settings.logger.debug(
                        f"Existing connection is stale: {e}, creating new connection"
                    )
                    # Clean up the stale connection
                    await self._cleanup_stale_session()
                    self.session = None
                    self.sse_client = None

            # Try to get upstream URL if we don't have it
            if not self._try_get_upstream_url():
                raise ValueError(
                    "Cannot get MCP upstream URL - PiecesOS may not be running"
                )

            try:
                Settings.logger.info(
                    f"Connecting to upstream MCP server at {self.upstream_url}"
                )
                self.sse_client = sse_client(self.upstream_url)
                read_stream, write_stream = await self.sse_client.__aenter__()

                session = ClientSession(read_stream, write_stream)
                await session.__aenter__()

                self.session = session

                self.tools = await session.list_tools()
                self.discovered_tools = [
                    tool[1] for tool in self.tools if tool[0] == "tools"
                ][0]

                Settings.logger.info(
                    f"Discovered {len(self.discovered_tools)} tools from upstream server"
                )

                # Save the discovered tools to cache for future offline use
                try:
                    cache_saved = self.cache_manager.save_tools_cache(
                        self.discovered_tools
                    )
                    if cache_saved:
                        Settings.logger.debug(
                            "Successfully updated tools cache with live data"
                        )
                    else:
                        Settings.logger.debug("Failed to save tools cache")
                except Exception as e:
                    Settings.logger.error(f"Error saving tools cache: {e}")

                return session

            except Exception as e:
                self.session = None
                Settings.logger.error(
                    f"Error connecting to upstream server: {e}", exc_info=True
                )
                raise

    async def cleanup(self):
        """Cleans up the upstream connection."""
        async with self.connection_lock:
            if self.session is not None:
                try:
                    session = self.session
                    sse = self.sse_client
                    self.session = None
                    self.sse_client = None

                    await session.__aexit__(None, None, None)
                    if sse:
                        await sse.__aexit__(None, None, None)
                    Settings.logger.info("Closed upstream connection")
                except Exception as e:
                    Settings.logger.error(
                        f"Error closing upstream connection: {e}", exc_info=True
                    )
                    sse = None
                    session = None

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
        self.server = Server(server_name)
        self.upstream = PosMcpConnection(upstream_url)
        self.setup_handlers()

    def setup_handlers(self):
        """Sets up the request handlers for the gateway server."""
        Settings.logger.info("Setting up gateway request handlers")

        @self.server.list_tools()
        async def list_tools() -> list[types.Tool]:
            Settings.logger.debug("Received list_tools request")

            # First, check if we already have discovered tools from a previous connection
            if self.upstream.discovered_tools:
                Settings.logger.debug(
                    f"Returning cached discovered tools: {len(self.upstream.discovered_tools)} tools"
                )
                return self.upstream.discovered_tools

            if Settings.pieces_client.is_pieces_running():
                await self.upstream.connect()
                Settings.logger.debug(
                    f"Successfully connected - returning {len(self.upstream.discovered_tools)} live tools"
                )
                return self.upstream.discovered_tools
            else:
                Settings.logger.debug("Returning cached/fallback tools")
                # Use the smart cache system that tries saved cache first, then hardcoded
                try:
                    fallback_tools = get_available_tools()
                    Settings.logger.debug(
                        f"Returning {len(fallback_tools)} cached/fallback tools"
                    )
                    return fallback_tools
                except Exception as cache_error:
                    Settings.logger.error(f"Couldn't get the cache {cache_error}")
                    return PIECES_MCP_TOOLS_CACHE

        @self.server.call_tool()
        async def call_tool(
            name: str, arguments: dict
        ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
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
            if self.upstream.upstream_url:
                try:
                    await self.upstream.connect()
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
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
        except Exception as e:
            Settings.logger.error(f"Error running gateway server: {e}", exc_info=True)
        finally:
            # Ensure we clean up the connection when the gateway exits
            Settings.logger.info("Gateway shutting down, cleaning up connections")
            await self.upstream.cleanup()


async def main():
    # Just initialize settings without starting services
    Settings.logger.info("Starting MCP Gateway")
    ltm_vision = LTMVisionWS(Settings.pieces_client, lambda x: None)
    health_ws = HealthWS(
        Settings.pieces_client, lambda x: None, lambda ws: ltm_vision.start()
    )

    # Try to get the MCP URL, but continue even if it fails
    upstream_url = None
    if Settings.pieces_client.is_pieces_running():
        upstream_url = get_mcp_latest_url()
        health_ws.start()

    gateway = MCPGateway(
        server_name="pieces-stdio-mcp",
        upstream_url=upstream_url,
    )

    await gateway.run()
