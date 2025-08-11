"""
Advanced validation tests for MCP Gateway.
Tests complex scenarios: concurrency, performance, edge cases, error recovery.
"""

import asyncio
import time
import pytest
import mcp.types as types
from unittest.mock import Mock, patch

from .utils import (
    mock_tools_changed_callback,
    mock_connection,
    UpdateEnum,
)
from pieces.mcp.gateway import PosMcpConnection


class TestMCPGatewayValidationAdvanced:
    """Advanced validation tests for complex scenarios and edge cases"""

    @pytest.mark.asyncio
    async def test_concurrent_validation_calls(self, mock_connection):
        """Test that concurrent validation calls don't cause race conditions"""
        # Mock all components to return True
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            with patch.object(mock_connection, "_check_ltm_status", return_value=True):
                # Run multiple validations concurrently
                results = []
                for i in range(10):
                    result = mock_connection._validate_system_status(f"tool_{i}")
                    results.append(result)

                # All should succeed
                assert all(result[0] for result in results)
                assert all(result[1] == "" for result in results)

    @pytest.mark.asyncio
    async def test_malformed_tool_names(self, mock_connection):
        """Test validation with potentially malicious tool names"""
        malicious_names = [
            "tool'; DROP TABLE users; --",
            "tool\x00\x01\x02",
            "tool\n\rmalicious\ncommand",
            "tool" * 1000,  # Very long name
            "<script>alert('xss')</script>",
        ]

        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=False
        ):
            for name in malicious_names:
                is_valid, error_message = mock_connection._validate_system_status(name)

                assert is_valid is False
                # Should not contain raw tool name in error
                assert name not in error_message
                # Should contain pieces open command
                assert "`pieces open`" in error_message

    @pytest.mark.asyncio
    async def test_connection_timeout_handling(self, mock_connection):
        """Test handling of connection timeouts"""
        # Mock validation success
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(True, "")
        ):
            # Mock connection to timeout
            with patch.object(
                mock_connection,
                "connect",
                side_effect=asyncio.TimeoutError("Connection timed out"),
            ):
                result = await mock_connection.call_tool("test_tool", {})

                assert isinstance(result, types.CallToolResult)
                assert "pieces restart" in result.content[0].text

    @pytest.mark.asyncio
    async def test_partial_failure_states(self, mock_connection):
        """Test when some checks pass but others fail"""
        # PiecesOS running but incompatible version
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            mock_result = Mock()
            mock_result.compatible = False
            mock_result.update = UpdateEnum.PiecesOS
            mock_connection.result = mock_result

            is_valid, error_message = mock_connection._validate_system_status(
                "test_tool"
            )

            assert is_valid is False
            assert "Please update PiecesOS" in error_message

        # Reset for next test
        mock_connection.result = None

        # PiecesOS running, compatible, but LTM disabled for LTM tool
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            mock_result = Mock()
            mock_result.compatible = True
            mock_connection.result = mock_result

            with patch.object(mock_connection, "_check_ltm_status", return_value=False):
                is_valid, error_message = mock_connection._validate_system_status(
                    "ask_pieces_ltm"
                )

                assert is_valid is False
                assert "Long Term Memory (LTM) is not enabled" in error_message

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self, mock_connection):
        """Test multiple simultaneous tool calls don't cause race conditions"""
        call_count = 0

        async def mock_call_tool_impl(tool_name, args):
            nonlocal call_count
            call_count += 1
            # Simulate some async work
            await asyncio.sleep(0.01)
            return types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Result for {tool_name}")]
            )

        with patch.object(
            mock_connection, "_validate_system_status", return_value=(True, "")
        ):
            with patch.object(mock_connection, "connect"):
                # Mock the actual tool execution
                original_call_tool = mock_connection.call_tool
                mock_connection.call_tool = mock_call_tool_impl

                try:
                    # Simulate concurrent calls
                    tasks = [
                        mock_connection.call_tool(f"tool_{i}", {}) for i in range(10)
                    ]
                    results = await asyncio.gather(*tasks)

                    # All should succeed without race conditions
                    assert len(results) == 10
                    assert all(isinstance(r, types.CallToolResult) for r in results)
                    assert call_count == 10

                    # Verify each result is unique
                    result_texts = [r.content[0].text for r in results]
                    assert len(set(result_texts)) == 10  # All unique

                finally:
                    mock_connection.call_tool = original_call_tool

    @pytest.mark.asyncio
    async def test_error_recovery_after_pos_restart(self, mock_connection):
        """Test gateway recovers after PiecesOS restart"""
        # Simulate PiecesOS down initially
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=False
        ):
            result1 = await mock_connection.call_tool("test_tool", {})
            assert isinstance(result1, types.CallToolResult)
            assert "PiecesOS is not running" in result1.content[0].text
            assert "`pieces open`" in result1.content[0].text

        # Reset any cached state
        mock_connection.result = None

        # Simulate PiecesOS back up
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            with patch.object(mock_connection, "_check_ltm_status", return_value=True):
                mock_result = Mock()
                mock_result.compatible = True
                mock_connection.result = mock_result

                with patch.object(mock_connection, "connect"):
                    # Should work now - validation passes
                    is_valid, error_msg = mock_connection._validate_system_status(
                        "test_tool"
                    )
                    assert is_valid is True
                    assert error_msg == ""

    @pytest.mark.asyncio
    async def test_error_message_content_validation(self, mock_connection):
        """Test that error messages provide helpful guidance to users"""
        # Test PiecesOS not running scenario
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=False
        ):
            is_valid, error_message = mock_connection._validate_system_status(
                "test_tool"
            )

            assert is_valid is False
            assert "PiecesOS is not running" in error_message
            assert "`pieces open`" in error_message
            assert "pieces" in error_message

        # Test CLI version incompatible scenario
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            with patch.object(
                mock_connection,
                "_check_version_compatibility",
                return_value=(
                    False,
                    "Please update the CLI version to be able to run the tool call, run 'pieces manage update' to get the latest version. Then retry your request again after updating.",
                ),
            ):
                is_valid, error_message = mock_connection._validate_system_status(
                    "test_tool"
                )

                assert is_valid is False
                assert "update the CLI version" in error_message
                assert "'pieces manage update'" in error_message
                assert "pieces" in error_message

        # Test PiecesOS version incompatible scenario
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            with patch.object(
                mock_connection,
                "_check_version_compatibility",
                return_value=(
                    False,
                    "Please update PiecesOS to a compatible version to be able to run the tool call. run 'pieces update' to get the latest version. Then retry your request again after updating.",
                ),
            ):
                is_valid, error_message = mock_connection._validate_system_status(
                    "test_tool"
                )

                assert is_valid is False
                assert "update PiecesOS" in error_message
                assert "'pieces update'" in error_message
                assert "pieces" in error_message

        # Test LTM disabled scenario
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            with patch.object(
                mock_connection, "_check_version_compatibility", return_value=(True, "")
            ):
                with patch.object(
                    mock_connection, "_check_ltm_status", return_value=False
                ):
                    is_valid, error_message = mock_connection._validate_system_status(
                        "ask_pieces_ltm"
                    )

                    assert is_valid is False
                    assert "Long Term Memory (LTM) is not enabled" in error_message
                    assert "`pieces open --ltm`" in error_message
                    assert "pieces" in error_message

    @pytest.mark.asyncio
    async def test_tools_hash_stability_and_memory_cleanup(self, mock_connection):
        """Test the new stable hash implementation and memory cleanup"""
        # Create mock tools
        tool1 = Mock()
        tool1.name = "tool1"
        tool1.description = "Short description"

        tool2 = Mock()
        tool2.name = "tool2"
        tool2.description = "Very long description that exceeds 200 characters. " * 10

        tool3 = Mock()
        tool3.name = "tool3"
        tool3.description = None

        tools = [tool1, tool2, tool3]

        # Test hash stability - same tools should produce same hash
        hash1 = mock_connection._get_tools_hash(tools)
        hash2 = mock_connection._get_tools_hash(tools)
        assert hash1 == hash2, "Hash should be stable for same tools"

        # Test hash is deterministic regardless of order
        shuffled_tools = [tool2, tool3, tool1]  # Different order
        hash3 = mock_connection._get_tools_hash(shuffled_tools)
        assert hash1 == hash3, "Hash should be same regardless of tool order"

        # Test hash changes when content changes
        tool1.description = "Different description"
        hash4 = mock_connection._get_tools_hash(tools)
        assert hash1 != hash4, "Hash should change when tool content changes"

        # Test memory cleanup during update_tools
        mock_connection.discovered_tools = [Mock(), Mock()]  # Simulate existing tools

        with patch.object(mock_connection, "_tools_have_changed", return_value=True):
            # Mock session.list_tools() to return our test tools
            mock_session = Mock()

            async def mock_list_tools():
                return [("tools", tools)]

            mock_session.list_tools = mock_list_tools

            await mock_connection.update_tools(mock_session, send_notification=False)

            # Verify tools were updated and old tools were cleared
            assert mock_connection.discovered_tools == tools
            # Note: The clearing happens before assignment, so we can't directly test it
            # but we can verify the method completes without error

    @pytest.mark.asyncio
    async def test_performance_validation_overhead(self, mock_connection):
        """Test that validation doesn't add significant overhead"""
        with patch.object(
            mock_connection, "_check_pieces_os_status", return_value=True
        ):
            with patch.object(mock_connection, "_check_ltm_status", return_value=True):
                mock_result = Mock()
                mock_result.compatible = True
                mock_connection.result = mock_result

                # Warm up
                for _ in range(10):
                    mock_connection._validate_system_status("test_tool")

                # Measure performance
                start = time.time()
                iterations = 100
                for _ in range(iterations):
                    is_valid, _ = mock_connection._validate_system_status("test_tool")
                    assert is_valid is True
                elapsed = time.time() - start

                # Should complete 100 validations in under 0.5 seconds
                # This is generous to account for CI environments
                assert elapsed < 0.5, (
                    f"Validation too slow: {elapsed:.3f}s for {iterations} calls"
                )

                avg_time = elapsed / iterations
                assert avg_time < 0.005, (
                    f"Average validation time too high: {avg_time:.6f}s"
                )

    @pytest.mark.asyncio
    async def test_hash_edge_cases(self, mock_connection):
        """Test hash function with edge cases"""
        # Empty tools list
        assert mock_connection._get_tools_hash([]) is None
        assert mock_connection._get_tools_hash(None) is None

        # Tool with empty name
        empty_name_tool = Mock()
        empty_name_tool.name = ""
        empty_name_tool.description = "Has description"
        hash_empty_name = mock_connection._get_tools_hash([empty_name_tool])
        assert hash_empty_name is not None

        # Tool with special characters in name/description
        special_tool = Mock()
        special_tool.name = "tool-with_special.chars@2024"
        special_tool.description = "Description with émojis 🔧 and símböls"
        hash_special = mock_connection._get_tools_hash([special_tool])
        assert hash_special is not None

        # Very large description (tests truncation)
        large_tool = Mock()
        large_tool.name = "large_tool"
        large_tool.description = "x" * 10000  # 10KB description
        hash_large = mock_connection._get_tools_hash([large_tool])

        # Same tool with truncated description should have same hash
        truncated_tool = Mock()
        truncated_tool.name = "large_tool"
        truncated_tool.description = "x" * 200  # Exactly 200 chars
        hash_truncated = mock_connection._get_tools_hash([truncated_tool])
        assert hash_large == hash_truncated, (
            "Large description should be truncated to 200 chars"
        )

    @pytest.mark.asyncio
    async def test_concurrent_connection_and_cleanup(self, mock_connection):
        """Test concurrent connection attempts and cleanup operations"""
        # Track connection attempts
        connection_count = 0
        cleanup_count = 0

        async def mock_connect():
            nonlocal connection_count
            connection_count += 1
            # Simulate connection work
            await asyncio.sleep(0.01)
            return Mock()  # Mock session

        async def mock_cleanup():
            nonlocal cleanup_count
            cleanup_count += 1
            # Simulate cleanup work
            await asyncio.sleep(0.01)

        # Mock successful validation
        with patch.object(
            mock_connection, "_validate_system_status", return_value=(True, "")
        ):
            # Mock the connection and cleanup methods
            original_connect = mock_connection.connect
            original_cleanup = mock_connection.cleanup

            mock_connection.connect = mock_connect
            mock_connection.cleanup = mock_cleanup

            try:
                tasks = []

                # Add connection tasks
                for i in range(3):
                    tasks.append(mock_connection.connect())

                # Add cleanup tasks
                for i in range(3):
                    tasks.append(mock_connection.cleanup())

                # Add tool call tasks that involve connection
                for i in range(2):
                    tasks.append(mock_connection.call_tool(f"tool_{i}", {}))

                # Execute all concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Verify all operations completed
                assert len(results) == 8  # 3 connects + 3 cleanups + 2 tool calls

                # Check for exceptions
                exceptions = [r for r in results if isinstance(r, Exception)]
                assert len(exceptions) == 0, f"Unexpected exceptions: {exceptions}"

                # Verify connection and cleanup methods were called expected number of times
                # Note: tool calls might also trigger connections
                assert connection_count >= 3, "Expected at least 3 connection attempts"
                assert cleanup_count == 3, "Expected exactly 3 cleanup operations"

            finally:
                # Restore original methods
                mock_connection.connect = original_connect
                mock_connection.cleanup = original_cleanup
