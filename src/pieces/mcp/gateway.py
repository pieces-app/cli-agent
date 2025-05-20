import asyncio
from pieces.mcp.utils import get_mcp_latest_url
from pieces.settings import Settings
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
        self.upstream_url = upstream_url
        self.session = None
        self.sse_client = None
        self.discovered_tools = []
        self.connection_lock = asyncio.Lock()

    async def connect(self):
        """Ensures a connection to the POS server exists and returns it."""
        async with self.connection_lock:
            if self.session is not None:
                Settings.logger.debug("Using existing upstream connection")
                return self.session

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
        try:
            Settings.logger.debug(f"Calling upstream tool: {name}")
            session = await self.connect()

            result = await session.call_tool(name, arguments)
            Settings.logger.debug(f"Successfully called tool: {name}")
            Settings.logger.debug(f"with results: {result}")
            return result

        except Exception as e:
            Settings.logger.error(f"Error calling POS MCP {name}: {e}", exc_info=True)
            # @mark-at-pieces not sure if there is a better way to return an error
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=str(e))]
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
            Settings.logger.debug(
                f"Discovered tools sent is {self.upstream.discovered_tools}"
            )
            return self.upstream.discovered_tools

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
            await self.upstream.connect()

            Settings.logger.info(f"Starting stdio server for {self.server.name}")
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name=self.server.name,
                        server_version="0.1.0",  # Do we need to use the cli-agent version here? @mark-at-pieces
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                    raise_exceptions=True,
                )
        except Exception as e:
            Settings.logger.error(f"Error running gateway server: {e}", exc_info=True)
        finally:
            # Ensure we clean up the connection when the gateway exits
            Settings.logger.info("Gateway shutting down, cleaning up connections")
            await self.upstream.cleanup()


async def main():
    Settings.pieces_client.open_pieces_os()
    Settings.startup()
    gateway = MCPGateway(
        server_name="pieces-stdio-mcp",
        upstream_url=get_mcp_latest_url(),
    )

    # Enable LTM
    Settings.pieces_client.copilot.context.ltm.ltm_status = Settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status()
    Settings.pieces_client.copilot.context.ltm.enable(True)

    await gateway.run()
