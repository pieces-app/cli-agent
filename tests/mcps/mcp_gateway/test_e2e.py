"""
End-to-end tests for the MCP Gateway using subprocess.
PiecesOS is required to run these tests.
LTM must be running, and PiecesOS as well.
"""

import pytest
import subprocess
import os
import json
import time

pytest.skip(
    "This module need you to sign in and POS must be running ignoring it in CI/CD",
    allow_module_level=True,
)
# TODO: Login to POS to proceed with that test


def run_mcp_command(args, timeout=10):
    """Helper function to run MCP commands and capture output."""
    cmd = ["pieces", "mcp"] + args
    env = os.environ.copy()

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, env=env
        )
        return result
    except subprocess.TimeoutExpired:
        return None
    except FileNotFoundError:
        # pieces command not found
        pytest.skip("pieces command not found in PATH")


def run_mcp_with_input(input_data, timeout=15):
    """Helper function to run MCP gateway and send input via stdin."""
    cmd = ["pieces", "mcp", "start"]
    env = os.environ.copy()

    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )

        stdout, stderr = process.communicate(input=input_data, timeout=timeout)
        return process.returncode, stdout, stderr
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Process timed out"
    except FileNotFoundError:
        # pieces command not found
        pytest.skip("pieces command not found in PATH")


class TestMCPGatewayE2E:
    """End-to-end tests for MCP Gateway subprocess interface."""

    def test_gateway_help_output(self):
        """Test that the gateway shows help information."""
        result = run_mcp_command(["--help"])

        if result is None:
            pytest.skip("Command timed out")

        # Check that we got some output (either stdout or stderr)
        assert result.stdout or result.stderr

        # The help output should mention 'mcp' or 'gateway'
        output = result.stdout + result.stderr
        assert "mcp" in output.lower() or "gateway" in output.lower()

    def test_gateway_startup_and_shutdown(self):
        """Test that the gateway can start up and shut down cleanly."""
        # Start the gateway process
        cmd = ["pieces", "mcp", "start"]
        env = os.environ.copy()

        try:
            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
            )
        except FileNotFoundError:
            pytest.skip("pieces command not found in PATH")

        # Give it a moment to start
        time.sleep(2)

        # Check if it's still running
        if process.poll() is None:
            # Process is running, terminate it
            process.terminate()
            try:
                # Increased timeout to handle the new cleanup lifecycle
                stdout, stderr = process.communicate(timeout=15)
                # Process terminated successfully
                assert True
            except subprocess.TimeoutExpired:
                # If normal terminate doesn't work, try with SIGKILL
                process.kill()
                try:
                    stdout, stderr = process.communicate(timeout=5)
                    # Process was killed, but this is acceptable for cleanup
                    assert True
                except subprocess.TimeoutExpired:
                    pytest.fail("Gateway did not terminate even with SIGKILL")
        else:
            # Process already exited
            stdout, stderr = process.communicate()
            # This might be expected if Pieces OS is not running
            # Check for expected error messages
            if "Pieces OS" in stderr or "MCP server" in stderr or "PiecesOS" in stderr:
                pytest.skip("Gateway exited due to missing dependencies")
            else:
                # Check if it's a normal exit (might happen if already running)
                if process.returncode == 0:
                    assert True
                else:
                    pytest.fail(
                        f"Gateway exited with code {process.returncode}. stderr: {stderr}"
                    )

    def test_gateway_json_rpc_initialize(self):
        """Test sending a JSON-RPC initialize request to the gateway."""
        # JSON-RPC 2.0 initialize request
        initialize_request = """{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test_client","version":"1.0.0"}}}"""
        initialize_request += "\n"  # Ensure newline for MCP input

        returncode, stdout, stderr = run_mcp_with_input(initialize_request, timeout=10)

        # Check if we got a response
        if returncode == -1:
            pytest.fail("Gateway timed out - this should not happen with POS running")

        # If we got output, try to parse it as JSON-RPC
        if stdout:
            lines = stdout.strip().split("\n")
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        # Check if it's a valid JSON-RPC response
                        assert "jsonrpc" in response
                        assert response["jsonrpc"] == "2.0"
                        # It should have either a result or an error
                        assert "result" in response or "error" in response
                        break
                    except json.JSONDecodeError:
                        # Not JSON, might be log output
                        continue
        elif "Pieces OS" in stderr or "MCP server" in stderr or "PiecesOS" in stderr:
            pytest.fail(
                f"Gateway requires Pieces OS to be running - but POS should be running. Error: {stderr}"
            )

    def test_gateway_json_rpc_list_tools(self):
        """Test sending a list tools request after initialization."""
        # Send both initialize and list_tools requests
        requests = [
            '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test-client","version":"1.0.0"}}}',
            '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}',
            '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}',
        ]

        input_data = "\n".join(requests) + "\n"
        returncode, stdout, stderr = run_mcp_with_input(input_data, timeout=10)

        if returncode == -1:
            pytest.fail("Gateway timed out - this should not happen with POS running")

        # Check for responses
        if stdout:
            lines = stdout.strip().split("\n")
            responses = []
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if "jsonrpc" in response:
                            responses.append(response)
                    except json.JSONDecodeError:
                        continue

            # We should have at least one response
            assert len(responses) > 0

            # Check if we got a tools list response
            tools_response = next((r for r in responses if r.get("id") == 2), None)
            if tools_response:
                if "result" in tools_response:
                    # Should have a tools array
                    assert "tools" in tools_response["result"]
                    assert isinstance(tools_response["result"]["tools"], list)
                elif "error" in tools_response:
                    # Error is acceptable if Pieces OS is not running
                    error_msg = tools_response["error"].get("message", "")
                    if (
                        "Pieces" not in error_msg
                        and "connection" not in error_msg.lower()
                    ):
                        pytest.fail(f"Unexpected error: {error_msg}")
        elif "Pieces OS" in stderr or "MCP server" in stderr or "PiecesOS" in stderr:
            pytest.fail(
                f"Gateway requires Pieces OS to be running - but POS should be running. Error: {stderr}"
            )

    def test_gateway_invalid_json_handling(self):
        """Test that the gateway handles invalid JSON gracefully."""
        invalid_inputs = [
            "not json at all",
            "{invalid json}",
            '{"jsonrpc": "2.0", "method": "unknown_method", "id": 1}',
            "",  # empty input
        ]

        for invalid_input in invalid_inputs:
            returncode, stdout, stderr = run_mcp_with_input(
                invalid_input + "\n", timeout=8
            )

            if returncode != -1:  # Not timed out
                if stdout:
                    lines = stdout.strip().split("\n")
                    for line in lines:
                        if line.strip():
                            try:
                                response = json.loads(line)
                                if "error" in response:
                                    assert (
                                        response["error"]["code"] < 0
                                    )  # Should be negative
                                    break
                            except json.JSONDecodeError:
                                continue

    def test_gateway_tool_call_response(self):
        """Test calling an actual tool and verifying the response."""
        # Create a complete session with init, list, and tool call
        session_input = []

        # Initialize
        session_input.append(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0.0"},
                    },
                    "id": 1,
                }
            )
        )

        # List tools
        session_input.append(
            json.dumps(
                {"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 2}
            )
        )

        # Call a tool (we'll use ask_pieces_ltm as it's likely to be available)
        session_input.append(
            json.dumps(
                {
                    "question": "What was I working on yesterday? What files did I modify, what tasks was I completing, and what was I focused on?",
                    "chat_llm": "claude-3-5-sonnet-20241022",
                    "connected_client": "Cursor",
                    "application_sources": ["Cursor", "Code"],
                    "topics": [
                        "yesterday",
                        "work",
                        "coding",
                        "files",
                        "tasks",
                        "progress",
                    ],
                    "related_questions": [
                        "What files did I edit yesterday?",
                        "What commits did I make yesterday?",
                        "What issues was I working on yesterday?",
                        "What features was I implementing yesterday?",
                    ],
                    "open_files": [],
                }
            )
        )

        # Send all requests
        input_data = "\n".join(session_input) + "\n"
        returncode, stdout, stderr = run_mcp_with_input(input_data, timeout=30)

        if returncode == -1:
            pytest.fail("Gateway timed out - this should not happen with POS running")

        if "Pieces OS" in stderr or "MCP server" in stderr or "PiecesOS" in stderr:
            pytest.fail(
                "Gateway requires Pieces OS to be running - but POS should be running"
            )

        # Parse all responses
        responses = {}
        if stdout:
            lines = stdout.strip().split("\n")
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if "id" in response:
                            responses[response["id"]] = response
                    except json.JSONDecodeError:
                        continue

        # Verify we got responses
        assert len(responses) > 0, "No valid JSON-RPC responses received"

        # Check initialization response
        if 1 in responses:
            init_resp = responses[1]
            assert "result" in init_resp or "error" in init_resp
            if "result" in init_resp:
                assert "protocolVersion" in init_resp["result"]

        # Check tools list response
        tools_available = False
        if 2 in responses:
            tools_resp = responses[2]
            if "result" in tools_resp and "tools" in tools_resp["result"]:
                tools = tools_resp["result"]["tools"]
                tools_available = len(tools) > 0

                # Verify tool structure
                for tool in tools:
                    assert "name" in tool
                    assert "description" in tool

        # Check tool call response
        if 3 in responses:
            tool_resp = responses[3]
            assert "result" in tool_resp or "error" in tool_resp

            if "result" in tool_resp:
                # Successful tool call
                assert "content" in tool_resp["result"]
                assert isinstance(tool_resp["result"]["content"], list)
                assert len(tool_resp["result"]["content"]) > 0
            elif "error" in tool_resp:
                # Error is acceptable (e.g., if LTM is not enabled)
                assert "code" in tool_resp["error"]
                assert "message" in tool_resp["error"]
        elif tools_available:
            # If we listed tools but didn't get a tool call response, that's a problem
            pytest.fail("Tools were listed but tool call did not return a response")

    def test_gateway_tool_call_simple(self):
        """Test a simple tool call flow with minimal validation."""
        # Build a proper MCP flow: init -> initialized notification -> list tools -> call tool
        session_requests = [
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0.0"},
                    },
                    "id": 1,
                }
            ),
            json.dumps(
                {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}
            ),
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": 2,
                }
            ),
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "ask_pieces_ltm",
                        "arguments": {"question": "Hello", "chat_llm": "gpt-4o-mini"},
                    },
                    "id": 3,
                }
            ),
        ]

        input_data = "\n".join(session_requests) + "\n"

        returncode, stdout, stderr = run_mcp_with_input(input_data, timeout=20)

        if returncode == -1:
            pytest.fail("Gateway timed out - this should not happen with POS running")

        if "Pieces OS" in stderr or "MCP server" in stderr or "PiecesOS" in stderr:
            pytest.fail(
                "Gateway requires Pieces OS to be running - but POS should be running"
            )

        responses = {}
        if stdout:
            lines = stdout.strip().split("\n")
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if "id" in response:
                            responses[response["id"]] = response
                    except json.JSONDecodeError:
                        continue

        assert len(responses) >= 1, f"Expected at least init response, got: {responses}"

        if 1 in responses:
            init_resp = responses[1]
            assert "result" in init_resp or "error" in init_resp
            if "result" in init_resp:
                assert "protocolVersion" in init_resp["result"]

        if 2 in responses:
            tools_resp = responses[2]
            if "result" in tools_resp:
                assert "tools" in tools_resp["result"]
                assert isinstance(tools_resp["result"]["tools"], list)

        if 3 in responses:
            tool_resp = responses[3]
            assert "result" in tool_resp or "error" in tool_resp

    def test_gateway_large_request_handling(self):
        """Test that the gateway can handle large requests."""
        large_text = "x" * 10000  # 10KB of text
        large_request = (
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "test_tool",
                        "arguments": {"large_param": large_text},
                    },
                    "id": 100,
                }
            )
            + "\n"
        )

        init_request = (
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0.0"},
                    },
                    "id": 1,
                }
            )
            + "\n"
        )

        input_data = init_request + large_request
        returncode, stdout, stderr = run_mcp_with_input(input_data, timeout=15)

        if returncode == -1:
            pytest.fail("Gateway timed out - this should not happen with POS running")

        assert stdout or stderr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
