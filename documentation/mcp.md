# MCP Gateway — Developer Documentation

## Overview

The MCP (Model Context Protocol) gateway enables IDE clients like Claude Desktop,
Cursor, and VS Code to communicate with PiecesOS tools through a standardized protocol.

## Architecture

```
                  stdio                    streamable HTTP
    IDE Client <--------> CLI Gateway <--------------------> PiecesOS
    (Claude,              (gateway.py)                       (MCP Server)
     Cursor, etc.)
```

### Components

| Component            | File             | Role                                   |
| -------------------- | ---------------- | -------------------------------------- |
| Gateway Server       | `gateway.py` `MCPGateway`        | stdio server, routes requests |
| Upstream Connection  | `gateway.py` `PosMcpConnection`  | manages PiecesOS connection   |
| URL Resolution       | `utils.py`                       | schema version selection, caching |
| CLI Handlers         | `handler.py`                     | `pieces mcp` subcommands      |
| IDE Integrations     | `integration.py`                 | config file management         |
| Fallback Tools       | `tools_cache.py`                 | offline tool definitions       |

## MCP Schema Versions

| Version      | Transport       | Endpoint Pattern                                  | Status    |
| ------------ | --------------- | ------------------------------------------------- | --------- |
| `2024-11-05` | SSE             | `/model_context_protocol/2024-11-05/sse`          | Legacy    |
| `2025-03-26` | Streamable HTTP | `/model_context_protocol/2025-03-26/mcp`          | Preferred |

The gateway prefers `2025-03-26` (streamable HTTP) for upstream connections because:

- Request-response model is more robust than long-lived SSE connections
- No connection degradation over 30–45 minute sessions
- Better error recovery and reconnection behavior

IDE integration configs (written to config files) still use `2024-11-05` SSE URLs
because IDEs connect directly to PiecesOS, not through the CLI gateway.

## Connection Lifecycle

1. **Startup**: `main()` initializes WebSockets (Health, Auth, LTM Vision),
   resolves the upstream URL, creates the gateway. Blocking SDK calls during
   health checks are offloaded to threads via `asyncio.to_thread()`.
2. **Connect**: `PosMcpConnection.connect()` creates a background task running
   `_connection_handler`, which enters the transport context manager and
   establishes a `ClientSession`
3. **Tool Discovery**: `update_tools()` fetches available tools, detects changes
   via SHA-256 hashing, and notifies the IDE client
4. **Request Proxying**: IDE sends `tools/call` via stdio → gateway forwards to
   PiecesOS via streamable HTTP → result returned to IDE
5. **Reconnection**: On connection failure, `connect()` cleans up stale state and
   creates a new connection task. URL cache is invalidated to handle PiecesOS restarts.
6. **Shutdown**: Signal handlers set `shutdown_event`, gateway cancels, WebSockets
   close, upstream connection cleans up

## URL Caching

Schema version URLs are cached in `utils._latest_urls` to avoid repeated API calls.
The cache is invalidated when:

- The upstream URL is `None` (PiecesOS wasn't running at startup)
- PiecesOS transitions from down to up (health check succeeds after failure)
- A connection is cleaned up (URL may be stale after disconnect)

## Validation Pipeline

Before every tool call, `_validate_system_status()` runs 4 checks:

1. **PiecesOS health** (via WebSocket)
2. **Version compatibility** (CLI vs PiecesOS)
3. **User authentication**
4. **LTM status** (for LTM-specific tools only)

Each check returns an actionable error message if it fails.

## Error Surfacing Philosophy

This is a CLI — errors must be surfaced to the user with actionable remediation
steps, not silently swallowed. The decision tree for every caught exception:

1. **Can we auto-retry?** → Retry with backoff
2. **Retry succeeded?** → Continue normally
3. **Retry failed or not retryable?** → Surface actionable error to user

Connection errors are stored in `_last_connection_error` so that the next
`call_tool` invocation includes them in the user-facing response. Tool call
errors include the specific exception type and message alongside remediation
commands like `pieces restart` or `pieces open`.

## Troubleshooting

| Symptom                                    | Likely Cause                              | Fix                                          |
| ------------------------------------------ | ----------------------------------------- | -------------------------------------------- |
| "PiecesOS is not running"                  | PiecesOS crashed or not started           | `pieces open`                                |
| Connection degrades after 30–45 min        | Using SSE instead of streamable HTTP      | Ensure `PREFERRED_SCHEMA_VERSION = "2025-03-26"` |
| Stale tools after PiecesOS restart         | URL cache not invalidated                 | Restart the CLI gateway                      |
| "Cannot get MCP upstream URL"              | PiecesOS not reachable                    | Check PiecesOS is running, check port        |
| Tool calls timeout                         | PiecesOS overloaded or network issues     | `pieces restart`                             |
| "Timed out connecting to PiecesOS"         | PiecesOS overloaded or restarting         | `pieces restart`                             |
| "Connection to PiecesOS was lost"          | PiecesOS shut down unexpectedly           | `pieces open`                                |
| "PiecesOS sent a malformed response"       | Version mismatch                          | `pieces update` then `pieces restart`        |

## Async Health Check

`_check_pieces_os_status` is fully async. Blocking SDK calls (health WebSocket
start, user snapshot, LTM status, etc.) are offloaded via `asyncio.to_thread()`
so the event loop is never stalled. An `asyncio.Lock` guards the fast-path
check to prevent redundant health probes.

## Notification Handling

The gateway uses the SDK's public `ClientSession(message_handler=...)` API to
receive upstream notifications. Only `ToolListChangedNotification` triggers
tool re-discovery and an IDE notification; all other message types are ignored
(the SDK handles them internally).

## Session ID Tracking

The `get_session_id` callable returned by `streamablehttp_client` is captured
and logged at connection establishment and included in Sentry breadcrumbs. This
aids debugging without adding functional complexity. The session ID is cleared
on connection cleanup.

## Known Limitations

- `_upstream_session_id` is logged for observability but not yet used for
  session resumption or reconnection.

## Testing

Tests live in `tests/mcps/mcp_gateway/`. Key test files:

| File                          | Description                                        |
| ----------------------------- | -------------------------------------------------- |
| `test_bug_fixes.py`           | Unit tests for connection lifecycle bugs           |
| `test_validation_core.py`     | System status validation tests                     |
| `test_validation_advanced.py` | Concurrency, edge cases, performance               |
| `test_integration.py`         | Integration tests (requires PiecesOS running)      |
| `test_e2e.py`                 | End-to-end subprocess tests (requires PiecesOS)    |
