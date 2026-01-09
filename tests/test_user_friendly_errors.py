"""
Tests for user-friendly error handling.
"""

from pieces.errors import (
    UserFriendlyError,
    ErrorCategory,
    format_error,
    get_user_friendly_message,
)


class TestUserFriendlyError:
    """Tests for the UserFriendlyError class."""
    
    def test_basic_error_creation(self):
        """Test creating a basic user-friendly error."""
        error = UserFriendlyError(
            title="Test error",
            reasons=["Reason 1", "Reason 2"],
            solutions=["Solution 1", "Solution 2"],
            help_link="https://example.com",
            category=ErrorCategory.CONNECTION,
        )
        
        assert error.title == "Test error"
        assert len(error.reasons) == 2
        assert len(error.solutions) == 2
        assert error.help_link == "https://example.com"
        assert error.category == ErrorCategory.CONNECTION
    
    def test_format_error_output(self):
        """Test that format_error produces expected output structure."""
        error = UserFriendlyError(
            title="Cannot connect to Pieces OS",
            reasons=["Pieces OS may not be running"],
            solutions=["Run: pieces open"],
            help_link="https://docs.pieces.app",
        )
        
        formatted = error.format_error()
        
        assert "❌ Cannot connect to Pieces OS" in formatted
        assert "Possible reasons:" in formatted
        assert "• Pieces OS may not be running" in formatted
        assert "Try these solutions:" in formatted
        assert "1. Run: pieces open" in formatted
        assert "📖 More help: https://docs.pieces.app" in formatted
    
    def test_format_error_with_technical_details(self):
        """Test that technical details are included when requested."""
        error = UserFriendlyError(
            title="Test error",
            technical_details="ConnectionRefusedError: [Errno 61]",
        )
        
        formatted_without = error.format_error(include_technical=False)
        formatted_with = error.format_error(include_technical=True)
        
        assert "ConnectionRefusedError" not in formatted_without
        assert "ConnectionRefusedError" in formatted_with
    
    def test_str_method(self):
        """Test that __str__ returns formatted output."""
        error = UserFriendlyError(title="Test error")
        assert str(error) == error.format_error()


class TestGetUserFriendlyMessage:
    """Tests for the get_user_friendly_message function."""
    
    def test_connection_refused_error(self):
        """Test handling of ConnectionRefusedError."""
        exception = ConnectionRefusedError("[Errno 61] Connection refused")
        friendly = get_user_friendly_message(exception)
        
        assert "connect" in friendly.title.lower()
        assert friendly.category == ErrorCategory.CONNECTION
        assert len(friendly.solutions) > 0
    
    def test_timeout_error(self):
        """Test handling of TimeoutError."""
        exception = TimeoutError("Operation timed out")
        friendly = get_user_friendly_message(exception)
        
        assert "timed out" in friendly.title.lower()
        assert friendly.category == ErrorCategory.TIMEOUT
    
    def test_permission_error(self):
        """Test handling of PermissionError."""
        exception = PermissionError("Permission denied")
        friendly = get_user_friendly_message(exception)
        
        assert "denied" in friendly.title.lower() or "permission" in friendly.title.lower()
        assert friendly.category == ErrorCategory.PERMISSION
    
    def test_file_not_found_error(self):
        """Test handling of FileNotFoundError."""
        exception = FileNotFoundError("File not found: test.txt")
        friendly = get_user_friendly_message(exception)
        
        assert "not found" in friendly.title.lower()
        assert friendly.category == ErrorCategory.NOT_FOUND
    
    def test_unknown_error_fallback(self):
        """Test that unknown errors get a reasonable fallback."""
        exception = Exception("Some unknown error")
        friendly = get_user_friendly_message(exception)
        
        assert friendly.title is not None
        assert friendly.category == ErrorCategory.UNKNOWN
        assert friendly.original_error == exception
    
    def test_websocket_error_pattern(self):
        """Test WebSocket error pattern matching."""
        exception = Exception("WebSocket connection failed: Connection refused")
        friendly = get_user_friendly_message(exception)
        
        assert friendly.category == ErrorCategory.CONNECTION
        assert "websocket" in friendly.title.lower() or "connect" in friendly.title.lower()
    
    def test_authentication_error_pattern(self):
        """Test authentication error pattern matching."""
        exception = Exception("401 Unauthorized: Invalid token")
        friendly = get_user_friendly_message(exception)
        
        assert friendly.category == ErrorCategory.AUTHENTICATION
    
    def test_rate_limit_error_pattern(self):
        """Test rate limit error pattern matching."""
        exception = Exception("429 Too Many Requests: Rate limit exceeded")
        friendly = get_user_friendly_message(exception)
        
        assert friendly.category == ErrorCategory.RATE_LIMIT
    
    def test_server_error_pattern(self):
        """Test server error pattern matching."""
        exception = Exception("500 Internal Server Error")
        friendly = get_user_friendly_message(exception)
        
        assert friendly.category == ErrorCategory.SERVER


class TestFormatError:
    """Tests for the format_error convenience function."""
    
    def test_format_error_convenience(self):
        """Test that format_error returns a string."""
        exception = ConnectionRefusedError("Connection refused")
        result = format_error(exception)
        
        assert isinstance(result, str)
        assert "❌" in result
    
    def test_format_error_with_technical(self):
        """Test format_error with technical details."""
        exception = ConnectionRefusedError("Connection refused")
        result = format_error(exception, include_technical=True)
        
        assert "Technical details:" in result


class TestErrorCategories:
    """Tests for error category classification."""
    
    def test_all_categories_exist(self):
        """Test that all expected categories exist."""
        categories = [
            ErrorCategory.CONNECTION,
            ErrorCategory.AUTHENTICATION,
            ErrorCategory.PERMISSION,
            ErrorCategory.NOT_FOUND,
            ErrorCategory.TIMEOUT,
            ErrorCategory.VERSION,
            ErrorCategory.CONFIGURATION,
            ErrorCategory.RATE_LIMIT,
            ErrorCategory.SERVER,
            ErrorCategory.UNKNOWN,
        ]
        
        for category in categories:
            assert category.value is not None


class TestRealWorldScenarios:
    """Integration-style tests for real-world error scenarios."""
    
    def test_pieces_os_not_running_scenario(self):
        """Test the scenario when Pieces OS is not running."""
        # Simulate the error that occurs when Pieces OS isn't running
        exception = ConnectionRefusedError("[Errno 61] Connection refused")
        formatted = format_error(exception)
        
        # Should mention Pieces OS
        assert "pieces" in formatted.lower() or "connect" in formatted.lower()
        # Should suggest running pieces open
        assert "pieces" in formatted.lower()
    
    def test_websocket_connection_failed_scenario(self):
        """Test the WebSocket connection failed scenario from the issue."""
        # This is the exact error type mentioned in the GitHub issue
        exception = Exception("WebSocket connection failed: [Errno 61] Connection refused")
        formatted = format_error(exception)
        
        # Verify it produces the expected user-friendly output
        assert "❌" in formatted
        assert "Possible reasons:" in formatted
        assert "Try these solutions:" in formatted
        assert "📖 More help:" in formatted
    
    def test_max_retry_error_scenario(self):
        """Test MaxRetryError scenario."""
        exception = Exception("MaxRetryError: Max retries exceeded with url")
        formatted = format_error(exception)
        
        assert "❌" in formatted
        assert len(formatted) > 50  # Should have substantial content
