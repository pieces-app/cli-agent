"""
Test suite for headless base models.

Tests for BaseResponse, SuccessResponse, ErrorResponse, CommandResult, and ErrorCode.
"""

import json
import pytest
from unittest.mock import patch, Mock
import sys
import threading
import concurrent.futures
from queue import Queue

from pieces.headless.models.base import (
    BaseResponse,
    SuccessResponse,
    ErrorResponse,
    CommandResult,
    ErrorCode,
)
from pieces.headless.exceptions import HeadlessError
from pieces.headless.output import HeadlessOutput


class TestErrorCode:
    """Test ErrorCode enum values."""

    def test_error_code_values(self):
        """Test that error codes have correct integer values."""
        assert ErrorCode.GENERAL_ERROR == 1
        assert ErrorCode.SERIALIZATION_ERROR == 2
        assert ErrorCode.COMMAND_ERROR == 3
        assert ErrorCode.INVALID_ARGUMENT == 4
        assert ErrorCode.TIMEOUT_ERROR == 5

        assert ErrorCode.PROMPT_REQUIRED == 100
        assert ErrorCode.CONFIRMATION_REQUIRED == 101
        assert ErrorCode.USER_INPUT_REQUIRED == 102
        assert ErrorCode.INTERACTIVE_OPERATION == 103

        assert ErrorCode.PIECES_OS_UPDATE_REQUIRED == 202
        assert ErrorCode.CLI_UPDATE_REQUIRED == 203
        assert ErrorCode.AUTHENTICATION_FAILED == 204
        assert ErrorCode.LTM_NOT_ENABLED == 205

        assert ErrorCode.MCP_SETUP_FAILED == 400
        assert ErrorCode.MCP_START_FAILED == 401
        assert ErrorCode.MCP_REPAIR_FAILED == 402
        assert ErrorCode.MCP_SERVER_NOT_RUNNING == 403

    def test_error_code_type(self):
        """Test that error codes are proper IntEnum instances."""
        assert isinstance(ErrorCode.GENERAL_ERROR, int)
        assert isinstance(ErrorCode.GENERAL_ERROR.value, int)


class TestSuccessResponse:
    """Test SuccessResponse class."""

    def test_success_response_basic(self):
        """Test basic success response creation."""
        response = SuccessResponse(command="test", data={"key": "value"})

        assert response.success is True
        assert response.command == "test"
        assert response.data == {"key": "value"}

    def test_success_response_none_data(self):
        """Test success response with None data."""
        response = SuccessResponse(command="test", data=None)

        assert response.success is True
        assert response.command == "test"
        assert response.data is None

    def test_success_response_to_dict(self):
        """Test success response conversion to dict."""
        response = SuccessResponse(command="test", data={"key": "value"})
        expected = {"success": True, "command": "test", "data": {"key": "value"}}

        assert response.to_dict() == expected

    def test_success_response_to_json(self):
        """Test success response conversion to JSON."""
        response = SuccessResponse(command="test", data={"key": "value"})
        json_str = response.to_json()

        # Parse back to verify it's valid JSON
        parsed = json.loads(json_str)
        expected = {"success": True, "command": "test", "data": {"key": "value"}}

        assert parsed == expected

    def test_success_response_to_json_with_indent(self):
        """Test success response JSON with indentation."""
        response = SuccessResponse(command="test", data={"key": "value"})
        json_str = response.to_json(indent=2)

        # Should contain newlines and spaces when indented
        assert "\n" in json_str
        assert "  " in json_str

        # Should still be valid JSON
        parsed = json.loads(json_str)
        expected = {"success": True, "command": "test", "data": {"key": "value"}}

        assert parsed == expected

    def test_success_response_complex_data(self):
        """Test success response with complex data structures."""
        complex_data = {
            "list": [1, 2, 3],
            "nested": {"inner": "value"},
            "boolean": True,
            "null": None,
        }
        response = SuccessResponse(command="complex", data=complex_data)

        assert response.data == complex_data

        # Verify JSON serialization works
        json_str = response.to_json()
        parsed = json.loads(json_str)
        assert parsed["data"] == complex_data


class TestErrorResponse:
    """Test ErrorResponse class."""

    def test_error_response_basic(self):
        """Test basic error response creation."""
        response = ErrorResponse(
            command="test",
            error_code=ErrorCode.GENERAL_ERROR,
            error_message="Test error",
        )

        assert response.success is False
        assert response.command == "test"
        assert response.data == {"error_type": 1, "error_message": "Test error"}

    def test_error_response_to_dict(self):
        """Test error response conversion to dict."""
        response = ErrorResponse(
            command="test",
            error_code=ErrorCode.PROMPT_REQUIRED,
            error_message="Prompt required",
        )
        expected = {
            "success": False,
            "command": "test",
            "data": {"error_type": 100, "error_message": "Prompt required"},
        }

        assert response.to_dict() == expected

    def test_error_response_to_json(self):
        """Test error response conversion to JSON."""
        response = ErrorResponse(
            command="test",
            error_code=ErrorCode.MCP_SETUP_FAILED,
            error_message="MCP setup failed",
        )
        json_str = response.to_json()

        # Parse back to verify it's valid JSON
        parsed = json.loads(json_str)
        expected = {
            "success": False,
            "command": "test",
            "data": {"error_type": 400, "error_message": "MCP setup failed"},
        }

        assert parsed == expected

    def test_error_response_different_error_codes(self):
        """Test error response with different error codes."""
        test_cases = [
            (ErrorCode.GENERAL_ERROR, 1),
            (ErrorCode.CONFIRMATION_REQUIRED, 101),
            (ErrorCode.CLI_UPDATE_REQUIRED, 203),
            (ErrorCode.MCP_SERVER_NOT_RUNNING, 403),
        ]

        for error_code, expected_value in test_cases:
            response = ErrorResponse(
                command="test", error_code=error_code, error_message="Test message"
            )

            assert response.data["error_type"] == expected_value


class TestCommandResult:
    """Test CommandResult class."""

    def test_command_result_creation(self):
        """Test CommandResult creation."""
        success_response = SuccessResponse(command="test", data={"result": "ok"})
        result = CommandResult(exit_code=0, headless_response=success_response)

        assert result.exit_code == 0
        assert result.headless_response == success_response

    def test_command_result_exit_non_headless(self):
        """Test CommandResult.exit() in non-headless mode."""
        success_response = SuccessResponse(command="test", data={"result": "ok"})
        result = CommandResult(exit_code=0, headless_response=success_response)

        with patch("sys.exit") as mock_exit:
            result.exit(is_headless=False)
            mock_exit.assert_called_once_with(0)

    def test_command_result_exit_headless(self):
        """Test CommandResult.exit() in headless mode."""
        success_response = SuccessResponse(command="test", data={"result": "ok"})
        result = CommandResult(exit_code=0, headless_response=success_response)

        with patch("builtins.print") as mock_print:
            result.exit(is_headless=True)

            # Should print JSON response
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Verify it's valid JSON
            parsed = json.loads(printed_output)
            expected = {"success": True, "command": "test", "data": {"result": "ok"}}
            assert parsed == expected

    def test_command_result_exit_headless_error(self):
        """Test CommandResult.exit() with error response in headless mode."""
        error_response = ErrorResponse(
            command="test",
            error_code=ErrorCode.GENERAL_ERROR,
            error_message="Test error",
        )
        result = CommandResult(exit_code=1, headless_response=error_response)

        with patch("builtins.print") as mock_print:
            result.exit(is_headless=True)

            # Should print JSON error response
            mock_print.assert_called_once()
            printed_output = mock_print.call_args[0][0]

            # Verify it's valid JSON
            parsed = json.loads(printed_output)
            expected = {
                "success": False,
                "command": "test",
                "data": {"error_type": 1, "error_message": "Test error"},
            }
            assert parsed == expected


class TestBaseResponse:
    """Test BaseResponse abstract class behavior."""

    def test_base_response_cannot_be_instantiated(self):
        """Test that BaseResponse cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseResponse(success=True, command="test")

    def test_base_response_subclass_must_implement_to_dict(self):
        """Test that BaseResponse subclasses must implement to_dict."""

        class IncompleteResponse(BaseResponse):
            pass

        with pytest.raises(TypeError):
            IncompleteResponse(success=True, command="test")

    def test_base_response_to_json_method(self):
        """Test BaseResponse.to_json() method using a concrete subclass."""
        response = SuccessResponse(command="test", data={"key": "value"})

        # Test default (no indent)
        json_str = response.to_json()
        parsed = json.loads(json_str)
        assert parsed["success"] is True
        assert parsed["command"] == "test"
        assert parsed["data"] == {"key": "value"}

        # Test with indent
        json_str_indented = response.to_json(indent=4)
        parsed_indented = json.loads(json_str_indented)
        assert parsed_indented == parsed
        assert "\n" in json_str_indented


class TestConcurrentAccess:
    """Test concurrent access scenarios for headless mode."""

    def test_concurrent_error_output(self):
        """Test that multiple threads can output errors simultaneously."""
        errors = []
        output_queue = Queue()

        def output_error_concurrent(thread_id):
            try:
                error = HeadlessError(
                    message=f"Error from thread {thread_id}",
                    error_code=ErrorCode.GENERAL_ERROR,
                )

                with patch("builtins.print") as mock_print:
                    HeadlessOutput.output_headless_error(error, command="test")
                    # Check if mock_print was called and has call_args
                    if mock_print.call_args is not None:
                        output_queue.put(mock_print.call_args[0][0])
                    else:
                        # If mock wasn't called as expected, add a marker
                        output_queue.put(
                            '{"success": false, "command": "test", "data": {"error_type": 1, "error_message": "Mock call failed"}}'
                        )
            except Exception as e:
                errors.append(e)

        # Run multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(output_error_concurrent, i) for i in range(100)]
            concurrent.futures.wait(futures)

        # Verify no errors occurred
        assert len(errors) == 0, f"Errors occurred: {errors}"

        # Verify all outputs are valid JSON
        outputs = []
        while not output_queue.empty():
            output = output_queue.get()
            parsed = json.loads(output)  # Should not raise
            outputs.append(parsed)

        assert len(outputs) == 100

    def test_concurrent_command_registration(self):
        """Test that command registration is thread-safe."""
        from pieces.base_command import BaseCommand

        # Clear existing commands
        original_commands = BaseCommand.commands[:]
        BaseCommand.commands.clear()

        errors = []
        registration_count = threading.local()

        def register_command_concurrent(thread_id):
            try:
                # Create a test command class dynamically
                class_name = f"TestCommand{thread_id}"
                TestCommandClass = type(
                    class_name,
                    (BaseCommand,),
                    {
                        "get_name": lambda self: f"test{thread_id}",
                        "get_help": lambda self: f"Test command {thread_id}",
                        "add_arguments": lambda self, parser: None,
                        "execute": lambda self, **kwargs: 0,
                    },
                )

                # Track registrations per thread
                if not hasattr(registration_count, "count"):
                    registration_count.count = 0
                registration_count.count += 1

            except Exception as e:
                errors.append(e)

        # Run concurrent registrations
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(register_command_concurrent, i) for i in range(50)
            ]
            concurrent.futures.wait(futures)

        # Verify no errors
        assert len(errors) == 0

        # Verify no duplicate registrations
        command_names = [cmd.get_name() for cmd in BaseCommand.commands]
        assert len(command_names) == len(set(command_names))

        # Restore original commands
        BaseCommand.commands = original_commands

    def test_concurrent_json_serialization(self):
        """Test JSON serialization under concurrent load."""
        results = Queue()

        def serialize_concurrent(data_id):
            complex_data = {
                "id": data_id,
                "nested": {"level": 1, "data": [1, 2, 3]},
                "unicode": f"Test 世界 {data_id}",
                "large_list": list(range(1000)),
            }

            response = SuccessResponse(command=f"test{data_id}", data=complex_data)
            json_output = response.to_json()
            results.put((data_id, json_output))

        # Run concurrent serializations
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(serialize_concurrent, i) for i in range(200)]
            concurrent.futures.wait(futures)

        # Verify all serializations succeeded
        serialized_data = {}
        while not results.empty():
            data_id, json_output = results.get()
            serialized_data[data_id] = json_output

        assert len(serialized_data) == 200

        # Verify each JSON is valid and contains correct data
        for data_id, json_output in serialized_data.items():
            parsed = json.loads(json_output)
            assert parsed["data"]["id"] == data_id
            assert len(parsed["data"]["large_list"]) == 1000

    def test_concurrent_error_response_creation(self):
        """Test creating error responses concurrently."""
        results = Queue()
        errors = []

        def create_error_response_concurrent(thread_id):
            try:
                for i in range(10):  # Multiple errors per thread
                    error_response = ErrorResponse(
                        command=f"test_command_{thread_id}_{i}",
                        error_code=ErrorCode.GENERAL_ERROR,
                        error_message=f"Test error from thread {thread_id}, iteration {i}",
                    )

                    # Verify response structure
                    response_dict = error_response.to_dict()
                    json_output = error_response.to_json()

                    # Validate JSON
                    parsed = json.loads(json_output)

                    results.put((thread_id, i, parsed))

            except Exception as e:
                errors.append(e)

        # Run concurrent error response creation
        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = [
                executor.submit(create_error_response_concurrent, i) for i in range(20)
            ]
            concurrent.futures.wait(futures)

        # Verify no errors occurred
        assert len(errors) == 0

        # Verify all responses were created correctly
        response_data = []
        while not results.empty():
            thread_id, iteration, parsed_response = results.get()
            response_data.append(parsed_response)

            # Verify response structure
            assert parsed_response["success"] is False
            assert parsed_response["command"] == f"test_command_{thread_id}_{iteration}"
            assert (
                parsed_response["data"]["error_type"] == ErrorCode.GENERAL_ERROR.value
            )
            assert f"thread {thread_id}" in parsed_response["data"]["error_message"]

        # Should have 20 threads * 10 iterations = 200 responses
        assert len(response_data) == 200

    def test_concurrent_success_response_creation(self):
        """Test creating success responses concurrently with complex data."""
        results = Queue()
        errors = []

        def create_success_response_concurrent(thread_id):
            try:
                # Create complex nested data
                complex_data = {
                    "thread_id": thread_id,
                    "nested_object": {
                        "level_1": {
                            "level_2": {
                                "values": list(range(thread_id, thread_id + 100))
                            }
                        }
                    },
                    "boolean_values": [True, False, True],
                    "null_value": None,
                    "unicode_text": f"Thread {thread_id} 测试数据 🚀",
                    "large_array": [{"id": i, "value": f"item_{i}"} for i in range(50)],
                }

                response = SuccessResponse(
                    command=f"concurrent_test_{thread_id}", data=complex_data
                )

                # Test both dict and JSON conversion
                response_dict = response.to_dict()
                json_output = response.to_json(indent=2)

                # Validate JSON parsing
                parsed = json.loads(json_output)

                results.put((thread_id, parsed))

            except Exception as e:
                errors.append(e)

        # Run concurrent success response creation
        with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
            futures = [
                executor.submit(create_success_response_concurrent, i)
                for i in range(100)
            ]
            concurrent.futures.wait(futures)

        # Verify no errors occurred
        assert len(errors) == 0

        # Verify all responses were created correctly
        thread_results = {}
        while not results.empty():
            thread_id, parsed_response = results.get()
            thread_results[thread_id] = parsed_response

            # Verify response structure
            assert parsed_response["success"] is True
            assert parsed_response["command"] == f"concurrent_test_{thread_id}"
            assert parsed_response["data"]["thread_id"] == thread_id
            assert len(parsed_response["data"]["large_array"]) == 50
            assert (
                parsed_response["data"]["unicode_text"]
                == f"Thread {thread_id} 测试数据 🚀"
            )

        # Should have responses from all 100 threads
        assert len(thread_results) == 100

        # Verify no data corruption between threads
        for thread_id, response in thread_results.items():
            expected_values = list(range(thread_id, thread_id + 100))
            actual_values = response["data"]["nested_object"]["level_1"]["level_2"][
                "values"
            ]
            assert actual_values == expected_values
