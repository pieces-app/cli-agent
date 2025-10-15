"""Test for the completion command functionality."""

import pytest
import io
import sys
from unittest.mock import patch, MagicMock, mock_open

from pieces.command_interface.completions import CompletionCommand


class TestCompletionCommand:
    """Tests for the CompletionCommand class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = CompletionCommand()

    def test_get_name(self):
        """Test that the command name is correct."""
        assert self.command.get_name() == "completion"

    def test_get_help(self):
        """Test that help text is provided."""
        help_text = self.command.get_help()
        assert "completion" in help_text.lower()

    def test_execute_dev_version(self):
        """Test execution in dev mode."""
        with patch("pieces.command_interface.completions.__version__", "dev"):
            result = self.command.execute(shell="bash")
            assert result == 3

    @patch("pieces.command_interface.completions.files")
    def test_show_completion_file_not_found(self, mock_files):
        """Test handling of missing completion file."""
        # Mock file not found
        mock_path = MagicMock()
        mock_path.read_text.side_effect = FileNotFoundError()
        mock_files.return_value.joinpath.return_value = mock_path

        result = self.command._show_completion("invalid_shell")
        assert result == 1

    @patch("pieces.command_interface.completions.files")
    def test_show_completion_large_content_windows_error(self, mock_files):
        """Test handling of Windows console limitation with large content."""
        # Create a very large content string
        large_content = "A" * 50000  # Large string that might cause Windows issues

        # Mock the file reading
        mock_path = MagicMock()
        mock_path.read_text.return_value = large_content
        mock_files.return_value.joinpath.return_value = mock_path

        # Mock print to raise OSError with errno 22
        def mock_print_error(*args, **kwargs):
            error = OSError("Invalid argument")
            error.errno = 22
            raise error

        with patch("builtins.print", side_effect=mock_print_error):
            # Mock sys.stdout.write to succeed
            with (
                patch("sys.stdout.write") as mock_write,
                patch("sys.stdout.flush") as mock_flush,
            ):
                result = self.command._show_completion("powershell")

                # Should succeed using the chunked fallback
                assert result == 0
                # Should have called sys.stdout.write with the content
                mock_write.assert_called_with(large_content)
                mock_flush.assert_called()

    @patch("pieces.command_interface.completions.files")
    def test_show_completion_other_os_error(self, mock_files):
        """Test that other OSErrors are properly re-raised."""
        # Mock the file reading
        mock_path = MagicMock()
        mock_path.read_text.return_value = "test content"
        mock_files.return_value.joinpath.return_value = mock_path

        # Mock print to raise different OSError
        def mock_print_error(*args, **kwargs):
            error = OSError("Different error")
            error.errno = 2  # Different errno
            raise error

        with patch("builtins.print", side_effect=mock_print_error):
            with pytest.raises(OSError) as exc_info:
                self.command._show_completion("bash")

            assert exc_info.value.errno == 2

    def test_write_content_chunked_success(self):
        """Test successful chunked writing."""
        content = "test content for chunked writing"

        with (
            patch("sys.stdout.write") as mock_write,
            patch("sys.stdout.flush") as mock_flush,
        ):
            self.command._write_content_chunked(content)

            mock_write.assert_called_once_with(content)
            mock_flush.assert_called()

    def test_write_content_chunked_fallback(self):
        """Test chunked writing fallback when sys.stdout.write fails."""
        content = "A" * 20000  # Content larger than default chunk size

        # Mock sys.stdout.write to fail first time
        def mock_write_fail_then_succeed(data):
            if not hasattr(mock_write_fail_then_succeed, "called"):
                mock_write_fail_then_succeed.called = True
                raise OSError("Write failed")
            return len(data)

        with (
            patch(
                "sys.stdout.write", side_effect=mock_write_fail_then_succeed
            ) as mock_write,
            patch("sys.stdout.flush") as mock_flush,
        ):
            self.command._write_content_chunked(content)

            # Should be called multiple times due to chunking fallback
            assert mock_write.call_count > 1
            assert mock_flush.call_count > 1

    def test_supported_shells(self):
        """Test that all expected shells are supported."""
        from pieces.command_interface.completions import supported_shells

        expected_shells = ["bash", "zsh", "fish", "powershell"]
        assert set(supported_shells) == set(expected_shells)
