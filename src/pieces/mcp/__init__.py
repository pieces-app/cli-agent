"""
Pieces MCP (Model Context Protocol) Gateway.

This package implements a gateway between IDE clients (via stdio) and PiecesOS
(via streamable HTTP / SSE). It handles:

- Connection lifecycle management (connect, reconnect, cleanup)
- Tool discovery and proxying (list_tools, call_tool)
- IDE integration configuration (Claude, Cursor, VS Code, etc.)
- Health monitoring and validation (PiecesOS status, version compat, LTM)

Architecture::

    IDE <--stdio--> MCPGateway <--streamable HTTP--> PiecesOS

Key modules:
    gateway     - Core gateway server and upstream connection management
    utils       - URL resolution and schema version selection
    handler     - CLI command handlers for ``pieces mcp`` subcommands
    integration - IDE-specific configuration file management
    tools_cache - Fallback tool definitions when PiecesOS is offline
"""

from .handler import handle_mcp, handle_mcp_docs, handle_repair, handle_status
from .list_mcp import handle_list, handle_list_headless
from .gateway import main as handle_gateway


__all__ = [
    "handle_mcp",
    "handle_mcp_docs",
    "handle_repair",
    "handle_status",
    "handle_list",
    "handle_list_headless",
    "handle_gateway",
]
