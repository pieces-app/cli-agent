"""
Core validation tests for MCP Gateway.
Tests basic validation flows: system status, version compatibility, LTM checks.
"""

import pytest
import mcp.types as types
from unittest.mock import Mock, patch

from .utils import (
    mock_tools_changed_callback,
    mock_connection,
    UpdateEnum,
)
from pieces.mcp.gateway import PosMcpConnection


class TestMCPGatewayValidationCore:
    """Core validation tests for basic system checks and validation flows"""

    @pytest.mark.asyncio
    async def test_validate_system_status_pieces_os_not_running(self, mock_connection):
        """Test validation when PiecesOS is not running"""
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=False
        ):
            is_valid, error_message = mock_connection._validate_system_status(
                "ask_pieces_ltm"
            )

            assert is_valid is False
            assert "PiecesOS is not running" in error_message
            assert "`pieces open`" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_version_incompatible_plugin_update(
        self, mock_connection
    ):
        """Test validation when CLI version needs updating"""
        # Mock PiecesOS running
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            # Mock version compatibility check to return plugin update needed
            mock_result = Mock()
            mock_result.compatible = False
            mock_result.update = UpdateEnum.Plugin
            mock_connection.result = mock_result

            is_valid, error_message = mock_connection._validate_system_status(
                "ask_pieces_ltm"
            )

            assert is_valid is False
            assert "Please update the CLI version" in error_message
            assert "pieces manage update" in error_message
            assert "retry your request again after updating" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_version_incompatible_pos_update(
        self, mock_connection
    ):
        """Test validation when PiecesOS version needs updating"""
        # Mock PiecesOS running
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            # Mock version compatibility check to return POS update needed
            mock_result = Mock()
            mock_result.compatible = False
            mock_result.update = UpdateEnum.PiecesOS  # Or any value that's not Plugin
            mock_connection.result = mock_result

            is_valid, error_message = mock_connection._validate_system_status(
                "ask_pieces_ltm"
            )

            assert is_valid is False
            assert "Please update PiecesOS" in error_message
            assert "pieces update" in error_message
            assert "retry your request again after updating" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_ltm_disabled(self, mock_connection):
        """Test validation when LTM is disabled for LTM tools"""
        # Mock PiecesOS running and version compatible
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Mock LTM disabled
            with patch.object(mock_connection, "_check_ltm_status", return_value=False):
                is_valid, error_message = mock_connection._validate_system_status(
                    "ask_pieces_ltm"
                )

                assert is_valid is False
                assert "Long Term Memory (LTM) is not enabled" in error_message
                assert "`pieces open --ltm`" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_ltm_disabled_create_memory_tool(
        self, mock_connection
    ):
        """Test validation when LTM is disabled for create_pieces_memory tool"""
        # Mock PiecesOS running and version compatible
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Mock LTM disabled
            with patch.object(mock_connection, "_check_ltm_status", return_value=False):
                is_valid, error_message = mock_connection._validate_system_status(
                    "create_pieces_memory"
                )

                assert is_valid is False
                assert "Long Term Memory (LTM) is not enabled" in error_message
                assert "`pieces open --ltm`" in error_message

    @pytest.mark.asyncio
    async def test_validate_system_status_non_ltm_tool_success(self, mock_connection):
        """Test validation success for non-LTM tools when LTM is disabled"""
        # Mock PiecesOS running and version compatible
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Mock LTM disabled (shouldn't matter for non-LTM tools)
            with patch.object(mock_connection, "_check_ltm_status", return_value=False):
                is_valid, error_message = mock_connection._validate_system_status(
                    "some_other_tool"
                )

                assert is_valid is True
                assert error_message == ""

    @pytest.mark.asyncio
    async def test_validate_system_status_all_checks_pass(self, mock_connection):
        """Test validation when all checks pass"""
        # Mock PiecesOS running
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            # Mock version compatible
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Mock LTM enabled
            with patch.object(mock_connection, "_check_ltm_status", return_value=True):
                is_valid, error_message = mock_connection._validate_system_status(
                    "ask_pieces_ltm"
                )

                assert is_valid is True
                assert error_message == ""

    @pytest.mark.asyncio
    async def test_call_tool_with_validation_failure(self, mock_connection):
        """Test call_tool returns error when validation fails"""
        # Mock validation failure
        error_msg = "Test validation error"
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(False, error_msg)
        ):
            result = await mock_connection.call_tool("test_tool", {})

            assert isinstance(result, types.CallToolResult)
            assert len(result.content) == 1
            assert isinstance(result.content[0], types.TextContent)
            assert result.content[0].text == error_msg

    @pytest.mark.asyncio
    async def test_call_tool_with_connection_failure(self, mock_connection):
        """Test call_tool handles connection failures gracefully"""
        # Mock validation success
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(True, "")
        ):
            # Mock connection failure
            with patch.object(
                mock_connection, "connect", side_effect=Exception("Connection failed")
            ):
                result = await mock_connection.call_tool("test_tool", {})

                assert isinstance(result, types.CallToolResult)
                assert len(result.content) == 1
                assert isinstance(result.content[0], types.TextContent)
                assert "`pieces restart`" in result.content[0].text

    @pytest.mark.asyncio
    async def test_get_error_message_for_tool_uses_validation(self, mock_connection):
        """Test that _get_error_message_for_tool uses the validation system"""
        # Mock validation failure
        error_msg = "Validation failed"
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(False, error_msg)
        ):
            result = mock_connection._get_error_message_for_tool("test_tool")

            assert result == error_msg

    @pytest.mark.asyncio
    async def test_get_error_message_for_tool_validation_passes(self, mock_connection):
        """Test _get_error_message_for_tool when validation passes but still has error"""
        # Mock validation success
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(True, "")
        ):
            result = mock_connection._get_error_message_for_tool("test_tool")

            assert "Unable to execute 'test_tool' tool" in result
            assert "`pieces restart`" in result

    def test_check_version_compatibility_caches_result(self, mock_connection):
        """Test that version compatibility check caches the result"""
        # Mock the VersionChecker
        with patch("pieces.mcp.gateway.VersionChecker") as mock_version_checker:
            mock_result = Mock()
            mock_result.compatible = True
            mock_version_checker.return_value.version_check.return_value = mock_result

            # First call
            is_compatible1, msg1 = mock_connection._check_version_compatibility()
            # Second call
            is_compatible2, msg2 = mock_connection._check_version_compatibility()

            # Should have cached the result
            assert mock_connection.result == mock_result
            assert is_compatible1 == is_compatible2
            assert is_compatible1 is True
            assert msg1 == msg2 == ""
            # VersionChecker should only be called once due to caching
            mock_version_checker.assert_called_once()

    @patch("pieces.mcp.gateway.HealthWS")
    def test_check_pieces_os_status_health_ws_running(
        self, mock_health_ws, mock_connection
    ):
        """Test _check_pieces_os_status when health WS is already running"""
        # Mock HealthWS.is_running() to return True
        mock_health_ws.is_running.return_value = True

        # Mock Settings.pieces_client.is_pos_stream_running
        with patch("pieces.mcp.gateway.Settings") as mock_settings:
            mock_settings.pieces_client.is_pos_stream_running = True

            result = mock_connection._check_pieces_os_status()

            assert result is True
            mock_health_ws.is_running.assert_called_once()

    @patch("pieces.mcp.gateway.HealthWS")
    @patch("pieces.mcp.gateway.Settings")
    def test_check_pieces_os_status_starts_health_ws(
        self, mock_settings, mock_health_ws, mock_connection
    ):
        """Test _check_pieces_os_status starts health WS when PiecesOS is running"""
        # Mock HealthWS.is_running() to return False initially
        mock_health_ws.is_running.return_value = False

        # Mock pieces_client.is_pieces_running() to return True
        mock_settings.pieces_client.is_pieces_running.return_value = True

        mock_health_ws_instance = Mock()
        mock_health_ws.get_instance.return_value = mock_health_ws_instance

        # Mock the workstream API call
        mock_settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status.return_value = Mock()

        result = mock_connection._check_pieces_os_status()

        assert result is True
        mock_health_ws_instance.start.assert_called_once()

    @patch("pieces.mcp.gateway.Settings")
    def test_check_ltm_status(self, mock_settings, mock_connection):
        """Test _check_ltm_status returns LTM enabled status"""
        mock_settings.pieces_client.copilot.context.ltm.is_enabled = True

        result = mock_connection._check_ltm_status()

        assert result is True

    @pytest.mark.asyncio
    async def test_multiple_validation_calls_same_tool(self, mock_connection):
        """Test that multiple validation calls for the same tool work correctly"""
        # Mock all components
        with (
            patch.object(mock_connection, "_check_pieces_os_status", return_value=True),
            patch.object(mock_connection, "_check_ltm_status", return_value=True),
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            # Call validation multiple times
            is_valid1, msg1 = mock_connection._validate_system_status("ask_pieces_ltm")
            is_valid2, msg2 = mock_connection._validate_system_status("ask_pieces_ltm")

            assert is_valid1 == is_valid2
            assert is_valid1 is True
            assert msg1 == msg2 == ""

    @pytest.mark.asyncio
    async def test_try_get_upstream_url_success(self, mock_connection):
        """Test _try_get_upstream_url when PiecesOS is running"""
        mock_connection.upstream_url = None

        with (
            patch("pieces.mcp.gateway.Settings") as mock_settings,
            patch(
                "pieces.mcp.gateway.get_mcp_latest_url", return_value="http://test-url"
            ),
        ):
            mock_settings.pieces_client.is_pieces_running.return_value = True

            result = mock_connection._try_get_upstream_url()

            assert result is True
            assert mock_connection.upstream_url == "http://test-url"

    @pytest.mark.asyncio
    async def test_try_get_upstream_url_failure(self, mock_connection):
        """Test _try_get_upstream_url when PiecesOS is not running"""
        mock_connection.upstream_url = None

        with patch("pieces.mcp.gateway.Settings") as mock_settings:
            mock_settings.pieces_client.is_pieces_running.return_value = False

            result = mock_connection._try_get_upstream_url()

            assert result is False
            assert mock_connection.upstream_url is None

    @pytest.mark.asyncio
    async def test_try_get_upstream_url_already_set(self, mock_connection):
        """Test _try_get_upstream_url when URL is already set"""
        mock_connection.upstream_url = "http://existing-url"

        result = mock_connection._try_get_upstream_url()

        assert result is True
        assert mock_connection.upstream_url == "http://existing-url"
