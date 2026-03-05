"""
Tests for MCP gateway bug fixes.

Covers: schema version selection, URL cache invalidation, cleanup ordering,
notification handler reconnection, polling early failure detection, resource
leak prevention, error surfacing, and session ping race conditions.
"""

import asyncio
import time
import pytest
import mcp.types as types
from unittest.mock import Mock, AsyncMock, patch

from .utils import mock_connection


# ---------------------------------------------------------------------------
# Bug 1: Schema version selection
# ---------------------------------------------------------------------------

class TestSchemaVersionSelection:
    """Verify that get_mcp_latest_url prefers 2025-03-26 streamable HTTP."""

    def _make_schema(self, version, endpoint):
        s = Mock()
        s.version = version
        s.entry_endpoint = endpoint
        return s

    @patch("pieces.mcp.utils._latest_urls", [])
    @patch("pieces.mcp.utils.Settings")
    def test_prefers_2025_03_26(self, mock_settings):
        from pieces.mcp.utils import get_mcp_latest_url, invalidate_mcp_url_cache

        invalidate_mcp_url_cache()
        schemas = [
            self._make_schema("2024-11-05", "http://localhost:39300/mcp/2024-11-05/sse"),
            self._make_schema("2025-03-26", "http://localhost:39300/mcp/2025-03-26/mcp"),
        ]
        mock_settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions.return_value = Mock(
            iterable=schemas
        )

        url = get_mcp_latest_url()
        assert url == "http://localhost:39300/mcp/2025-03-26/mcp"
        invalidate_mcp_url_cache()

    @patch("pieces.mcp.utils._latest_urls", [])
    @patch("pieces.mcp.utils.Settings")
    def test_falls_back_to_first(self, mock_settings):
        from pieces.mcp.utils import get_mcp_latest_url, invalidate_mcp_url_cache

        invalidate_mcp_url_cache()
        schemas = [
            self._make_schema("2024-11-05", "http://localhost:39300/mcp/2024-11-05/sse"),
        ]
        mock_settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions.return_value = Mock(
            iterable=schemas
        )

        url = get_mcp_latest_url()
        assert url == "http://localhost:39300/mcp/2024-11-05/sse"
        invalidate_mcp_url_cache()

    @patch("pieces.mcp.utils._latest_urls", [])
    @patch("pieces.mcp.utils.Settings")
    def test_empty_list_raises(self, mock_settings):
        from pieces.mcp.utils import get_mcp_latest_url, invalidate_mcp_url_cache

        invalidate_mcp_url_cache()
        mock_settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions.return_value = Mock(
            iterable=[]
        )

        with pytest.raises(ValueError, match="No MCP schema versions"):
            get_mcp_latest_url()
        invalidate_mcp_url_cache()

    @patch("pieces.mcp.utils._latest_urls", [])
    @patch("pieces.mcp.utils.Settings")
    def test_get_mcp_sse_url_returns_sse(self, mock_settings):
        from pieces.mcp.utils import get_mcp_sse_url, invalidate_mcp_url_cache

        invalidate_mcp_url_cache()
        schemas = [
            self._make_schema("2025-03-26", "http://localhost:39300/mcp/2025-03-26/mcp"),
            self._make_schema("2024-11-05", "http://localhost:39300/mcp/2024-11-05/sse"),
        ]
        mock_settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions.return_value = Mock(
            iterable=schemas
        )

        url = get_mcp_sse_url()
        assert url == "http://localhost:39300/mcp/2024-11-05/sse"
        invalidate_mcp_url_cache()


# ---------------------------------------------------------------------------
# Bug 2: URL cache invalidation
# ---------------------------------------------------------------------------

class TestCacheInvalidation:
    """Verify that invalidate_mcp_url_cache clears the cache."""

    @patch("pieces.mcp.utils.Settings")
    def test_invalidate_forces_refetch(self, mock_settings):
        from pieces.mcp.utils import get_mcp_model_urls, invalidate_mcp_url_cache

        invalidate_mcp_url_cache()
        schema = Mock()
        schema.version = "2025-03-26"
        schema.entry_endpoint = "http://test/mcp"
        mock_settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions.return_value = Mock(
            iterable=[schema]
        )

        get_mcp_model_urls()
        assert mock_settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions.call_count == 1

        get_mcp_model_urls()
        assert mock_settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions.call_count == 1

        invalidate_mcp_url_cache()
        get_mcp_model_urls()
        assert mock_settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions.call_count == 2

        invalidate_mcp_url_cache()

    @pytest.mark.asyncio
    async def test_try_get_upstream_url_invalidates_when_none(self, mock_connection):
        mock_connection.upstream_url = None

        with (
            patch("pieces.mcp.gateway.Settings") as mock_settings,
            patch("pieces.mcp.gateway.get_mcp_latest_url", return_value="http://new-url/mcp"),
            patch("pieces.mcp.gateway.invalidate_mcp_url_cache") as mock_invalidate,
        ):
            mock_settings.pieces_client.is_pieces_running.return_value = True

            result = mock_connection._try_get_upstream_url()

            assert result is True
            assert mock_connection.upstream_url == "http://new-url/mcp"
            mock_invalidate.assert_called_once()


# ---------------------------------------------------------------------------
# Bug 3: Cleanup ordering
# ---------------------------------------------------------------------------

class TestCleanupOrdering:
    """Verify __aexit__ is called before instance vars are nullified."""

    @pytest.mark.asyncio
    async def test_aexit_called_before_nullify(self, mock_connection):
        session_mock = AsyncMock()
        transport_mock = AsyncMock()
        mock_connection.session = session_mock
        mock_connection._transport_ctx = transport_mock

        call_order = []

        async def session_aexit(*args):
            assert mock_connection.session is session_mock, \
                "session should still be set when __aexit__ is called"
            call_order.append("session_aexit")

        async def transport_aexit(*args):
            call_order.append("transport_aexit")

        session_mock.__aexit__ = session_aexit
        transport_mock.__aexit__ = transport_aexit

        await mock_connection._cleanup_stale_session()

        assert mock_connection.session is None
        assert mock_connection._transport_ctx is None
        assert "session_aexit" in call_order
        assert "transport_aexit" in call_order

    @pytest.mark.asyncio
    async def test_cleanup_continues_on_aexit_exception(self, mock_connection):
        session_mock = AsyncMock()
        transport_mock = AsyncMock()
        mock_connection.session = session_mock
        mock_connection._transport_ctx = transport_mock

        session_mock.__aexit__ = AsyncMock(side_effect=RuntimeError("boom"))
        transport_mock.__aexit__ = AsyncMock()

        await mock_connection._cleanup_stale_session()

        assert mock_connection.session is None
        assert mock_connection._transport_ctx is None
        transport_mock.__aexit__.assert_called_once()


# ---------------------------------------------------------------------------
# Bug 4: Notification handler (now via public message_handler API)
# ---------------------------------------------------------------------------

class TestMessageHandler:
    """Verify _make_message_handler uses the public SDK API correctly."""

    @pytest.mark.asyncio
    async def test_each_call_returns_distinct_handler(self, mock_connection):
        handler1 = mock_connection._make_message_handler(send_notification=True)
        handler2 = mock_connection._make_message_handler(send_notification=True)

        assert handler1 is not handler2

    @pytest.mark.asyncio
    async def test_handles_tool_list_changed_notification(self, mock_connection):
        mock_session = AsyncMock()
        mock_connection.session = mock_session
        mock_connection._tools_changed_callback = AsyncMock()

        handler = mock_connection._make_message_handler(send_notification=True)

        notification = types.ServerNotification(
            root=types.ToolListChangedNotification(
                method="notifications/tools/list_changed"
            )
        )

        with patch.object(mock_connection, "update_tools", new_callable=AsyncMock):
            await handler(notification)

        mock_connection._tools_changed_callback.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_ignores_non_notification_messages(self, mock_connection):
        handler = mock_connection._make_message_handler(send_notification=True)
        mock_connection._tools_changed_callback = AsyncMock()

        await handler("not a notification")
        await handler(Exception("some error"))
        await handler(42)

        mock_connection._tools_changed_callback.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_no_stale_main_handler_attribute(self, mock_connection):
        mock_connection._make_message_handler(send_notification=True)

        assert not hasattr(mock_connection, "main_notification_handler")


# ---------------------------------------------------------------------------
# Bug 5: Polling early failure detection
# ---------------------------------------------------------------------------

class TestPollingEarlyExit:
    """Verify connect() detects early task failure instead of timing out."""

    @pytest.mark.asyncio
    async def test_detects_early_task_failure(self, mock_connection):
        mock_connection.upstream_url = "http://test/mcp"

        with patch.object(mock_connection, "_ensure_clean_state", new_callable=AsyncMock):
            with patch.object(
                mock_connection,
                "_connection_handler",
                side_effect=RuntimeError("immediate failure"),
            ):
                start = time.time()
                with pytest.raises(RuntimeError, match="immediate failure"):
                    await mock_connection.connect()
                elapsed = time.time() - start

                assert elapsed < 3.0, (
                    f"connect() should fail fast, not wait 10s (took {elapsed:.1f}s)"
                )


# ---------------------------------------------------------------------------
# Bug 6: Resource leaks
# ---------------------------------------------------------------------------

class TestResourceLeaks:
    """Verify bare except is replaced and resources are cleaned up."""

    def test_try_get_upstream_url_does_not_catch_system_exit(self, mock_connection):
        mock_connection.upstream_url = None

        with patch("pieces.mcp.gateway.Settings") as mock_settings:
            mock_settings.pieces_client.is_pieces_running.return_value = True

            with patch(
                "pieces.mcp.gateway.get_mcp_latest_url",
                side_effect=SystemExit(1),
            ):
                with pytest.raises(SystemExit):
                    mock_connection._try_get_upstream_url()


# ---------------------------------------------------------------------------
# Bug 9: Session ping race
# ---------------------------------------------------------------------------

class TestSessionPingRace:
    """Verify connect() handles session nullified during ping."""

    @pytest.mark.asyncio
    async def test_handles_session_nullified_during_ping(self, mock_connection):
        mock_connection.upstream_url = "http://test/mcp"

        mock_session = AsyncMock()
        mock_session.send_ping = AsyncMock(side_effect=Exception("session gone"))
        mock_connection.session = mock_session
        mock_connection._connection_task = Mock()
        mock_connection._connection_task.done.return_value = False

        with (
            patch.object(mock_connection, "_ensure_clean_state", new_callable=AsyncMock),
            patch.object(mock_connection, "_connection_handler", new_callable=AsyncMock) as mock_handler,
        ):
            async def fake_handler(send_notification=True):
                mock_connection.session = AsyncMock()
                await asyncio.sleep(10)

            mock_handler.side_effect = fake_handler

            session = await mock_connection.connect()
            assert session is not None


# ---------------------------------------------------------------------------
# Bug 11: Error surfacing
# ---------------------------------------------------------------------------

class TestErrorSurfacing:
    """Verify errors are surfaced to users with actionable messages."""

    @pytest.mark.asyncio
    async def test_call_tool_timeout_includes_specific_error(self, mock_connection):
        with patch.object(
            mock_connection, "_validate_system_status", new=AsyncMock(return_value=(True, ""))
        ):
            with patch.object(
                mock_connection,
                "connect",
                side_effect=TimeoutError("timed out"),
            ):
                result = await mock_connection.call_tool("test_tool", {})

                assert isinstance(result, types.CallToolResult)
                text = result.content[0].text
                assert "Timed out" in text
                assert "pieces restart" in text

    @pytest.mark.asyncio
    async def test_call_tool_connection_error_includes_pieces_open(self, mock_connection):
        with patch.object(
            mock_connection, "_validate_system_status", new=AsyncMock(return_value=(True, ""))
        ):
            with patch.object(
                mock_connection,
                "connect",
                side_effect=ConnectionError("refused"),
            ):
                result = await mock_connection.call_tool("test_tool", {})

                assert isinstance(result, types.CallToolResult)
                text = result.content[0].text
                assert "pieces open" in text
                assert "refused" in text

    @pytest.mark.asyncio
    async def test_call_tool_generic_error_includes_details(self, mock_connection):
        with patch.object(
            mock_connection, "_validate_system_status", new=AsyncMock(return_value=(True, ""))
        ):
            with patch.object(
                mock_connection,
                "connect",
                side_effect=RuntimeError("something broke"),
            ):
                result = await mock_connection.call_tool("test_tool", {})

                assert isinstance(result, types.CallToolResult)
                text = result.content[0].text
                assert "RuntimeError" in text
                assert "something broke" in text

    @pytest.mark.asyncio
    async def test_last_connection_error_surfaced(self, mock_connection):
        mock_connection._last_connection_error = (
            "Connection to PiecesOS timed out (ReadTimeout)."
        )

        with patch.object(
            mock_connection, "_validate_system_status", new=AsyncMock(return_value=(True, ""))
        ):
            with patch.object(
                mock_connection,
                "connect",
                side_effect=Exception("generic"),
            ):
                result = await mock_connection.call_tool("test_tool", {})

                text = result.content[0].text
                assert "ReadTimeout" in text

    @pytest.mark.asyncio
    async def test_last_connection_error_cleared_on_success(self, mock_connection):
        mock_connection._last_connection_error = "old error"
        mock_connection.upstream_url = "http://test/mcp"

        mock_session = AsyncMock()

        with (
            patch.object(mock_connection, "_ensure_clean_state", new_callable=AsyncMock),
            patch.object(mock_connection, "_connection_handler", new_callable=AsyncMock) as mock_handler,
        ):
            async def fake_handler(send_notification=True):
                mock_connection.session = mock_session
                mock_connection._last_connection_error = None
                await asyncio.sleep(10)

            mock_handler.side_effect = fake_handler

            session = await mock_connection.connect()
            assert session is mock_session
            assert mock_connection._last_connection_error is None

    @pytest.mark.asyncio
    async def test_list_tools_fallback_logs_warning(self):
        from pieces.mcp.gateway import MCPGateway

        with (
            patch("pieces.mcp.gateway.Settings") as mock_settings,
            patch("pieces.mcp.gateway.Server"),
            patch("pieces.mcp.gateway.sentry_sdk"),
        ):
            mock_settings.logger = Mock()
            gateway = MCPGateway(
                server_name="test",
                upstream_url="http://test/mcp",
            )

            gateway.upstream._check_pieces_os_status = AsyncMock(return_value=False)
            gateway.upstream.discovered_tools = []

            handlers = {}
            original_list_tools = gateway.server.list_tools

            def capture_list_tools():
                def decorator(func):
                    handlers["list_tools"] = func
                    return func
                return decorator

            gateway.server.list_tools = capture_list_tools
            gateway.server.call_tool = lambda: lambda f: f
            gateway.setup_handlers()

            if "list_tools" in handlers:
                result = await handlers["list_tools"]()
                mock_settings.logger.warning.assert_called()
                warning_msg = mock_settings.logger.warning.call_args[0][0]
                assert "pieces open" in warning_msg.lower() or "PiecesOS" in warning_msg


# ---------------------------------------------------------------------------
# Enhancement 1: asyncio.Lock + asyncio.to_thread in _check_pieces_os_status
# ---------------------------------------------------------------------------

class TestAsyncHealthCheck:
    """Verify _check_pieces_os_status is async and uses to_thread."""

    @pytest.mark.asyncio
    @patch("pieces.mcp.gateway.HealthWS")
    async def test_returns_true_when_health_ws_running(
        self, mock_health_ws, mock_connection
    ):
        mock_health_ws.is_running.return_value = True
        with patch("pieces.mcp.gateway.Settings") as mock_settings:
            mock_settings.pieces_client.is_pos_stream_running = True

            result = await mock_connection._check_pieces_os_status()

            assert result is True

    @pytest.mark.asyncio
    async def test_returns_false_when_pieces_not_running(self, mock_connection):
        with (
            patch("pieces.mcp.gateway.HealthWS") as mock_health_ws,
            patch("pieces.mcp.gateway.Settings") as mock_settings,
        ):
            mock_health_ws.is_running.return_value = False
            mock_settings.pieces_client.is_pos_stream_running = False
            mock_settings.pieces_client.is_pieces_running.return_value = False

            result = await mock_connection._check_pieces_os_status()

            assert result is False

    @pytest.mark.asyncio
    async def test_offloads_blocking_calls_to_thread(self, mock_connection):
        with (
            patch("pieces.mcp.gateway.HealthWS") as mock_health_ws,
            patch("pieces.mcp.gateway.Settings") as mock_settings,
            patch("pieces.mcp.gateway.sentry_sdk"),
            patch("asyncio.to_thread", new_callable=AsyncMock) as mock_to_thread,
        ):
            mock_health_ws.is_running.return_value = False
            mock_settings.pieces_client.is_pos_stream_running = False

            mock_to_thread.side_effect = [
                True,   # is_pieces_running
                None,   # health_ws.start
                "id1",  # get_os_id
                Mock(user=Mock()),  # user_snapshot
                Mock(),  # vision_status
            ]

            mock_health_ws.get_instance.return_value = Mock()

            result = await mock_connection._check_pieces_os_status()

            assert result is True
            assert mock_to_thread.call_count == 5

    @pytest.mark.asyncio
    async def test_uses_asyncio_lock_not_threading_lock(self, mock_connection):
        assert isinstance(mock_connection._health_check_lock, asyncio.Lock)

    @pytest.mark.asyncio
    async def test_validate_system_status_is_async(self, mock_connection):
        import inspect
        assert inspect.iscoroutinefunction(mock_connection._validate_system_status)

    @pytest.mark.asyncio
    async def test_get_error_message_for_tool_is_async(self, mock_connection):
        import inspect
        assert inspect.iscoroutinefunction(mock_connection._get_error_message_for_tool)


# ---------------------------------------------------------------------------
# Enhancement 3: get_session_id captured for observability
# ---------------------------------------------------------------------------

class TestSessionIdTracking:
    """Verify upstream session ID is captured and logged."""

    def test_upstream_session_id_initialized_to_none(self, mock_connection):
        assert mock_connection._upstream_session_id is None

    @pytest.mark.asyncio
    async def test_session_id_cleared_on_cleanup(self, mock_connection):
        mock_connection._upstream_session_id = "test-session-123"
        mock_connection.session = None
        mock_connection._transport_ctx = None

        await mock_connection._cleanup_stale_session()

        assert mock_connection._upstream_session_id is None
