"""
Test suite for the Logger class.

Tests for logger functionality in both headless and non-headless modes,
including logging, prompts, and file handling.
"""

import pytest
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from pieces.logger import Logger
from pieces.headless.exceptions import HeadlessPromptError
from pieces.settings import Settings


@patch("pieces.logger.Console")
@patch("pieces.logger.prompt.Confirm")
@patch("pieces.logger.Prompt")
class TestLogger:
    """Test Logger class functionality."""

    def setup_method(self, method):
        """Reset Logger singleton before each test."""
        Logger._instance = None

    def teardown_method(self, method):
        """Clean up after each test."""
        Logger._instance = None

    def test_logger_init_debug_mode_false(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test logger initialization with debug mode disabled."""
        logger = Logger(debug_mode=False)

        assert logger.name == "Pieces_CLI"
        assert logger.debug_mode is False
        assert logger.logger.level == logging.ERROR
        assert logger.console is not None
        assert logger.console_error is not None

    def test_logger_init_debug_mode_true(self, mock_prompt, mock_confirm, mock_console):
        """Test logger initialization with debug mode enabled."""
        logger = Logger(debug_mode=True)

        assert logger.debug_mode is True
        assert logger.logger.level == logging.DEBUG

    def test_logger_init_with_log_dir(self, mock_prompt, mock_confirm, mock_console):
        """Test logger initialization with log directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = Logger(debug_mode=True, log_dir=temp_dir)

            # Check that file handler was created
            assert hasattr(logger, "file_handler")
            assert isinstance(logger.file_handler, logging.FileHandler)

            # Check that log file was created
            log_files = list(Path(temp_dir, "logs").glob("*.log"))
            assert len(log_files) > 0

            # Check filename format
            expected_date = datetime.today().strftime("%Y%m%d")
            expected_filename = f"Pieces_CLI_{expected_date}.log"
            assert any(log_file.name == expected_filename for log_file in log_files)

    def test_setup_file_logging(self, mock_prompt, mock_confirm, mock_console):
        """Test file logging setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = Logger()
            logger._setup_file_logging(temp_dir, "TestLogger")

            # Check that file handler exists
            assert hasattr(logger, "file_handler")
            assert isinstance(logger.file_handler, logging.FileHandler)

            # Check that handler was added to logger
            assert logger.file_handler in logger.logger.handlers

    def test_logging_methods(self, mock_prompt, mock_confirm, mock_console):
        """Test all logging methods."""
        logger = Logger(debug_mode=True)

        with (
            patch.object(logger.logger, "info") as mock_info,
            patch.object(logger.logger, "error") as mock_error,
            patch.object(logger.logger, "debug") as mock_debug,
        ):
            # Test info logging
            logger.info("Info message")
            mock_info.assert_called_once_with("Info message")

            # Test error logging
            logger.error("Error message")
            mock_error.assert_called_once_with("Error message", exc_info=True)

            # Test debug logging
            logger.debug("Debug message")
            mock_debug.assert_called_once_with("Debug message")

            # Test critical logging (should call error)
            mock_error.reset_mock()
            logger.critical("Critical message")
            mock_error.assert_called_once_with("Critical message", exc_info=True)

    def test_logging_with_custom_exc_info(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test logging methods with custom exc_info parameter."""
        logger = Logger()

        with patch.object(logger.logger, "error") as mock_error:
            # Test error with custom exc_info
            logger.error("Error message", exc_info=False)
            mock_error.assert_called_once_with("Error message", exc_info=False)

            # Test critical with custom exc_info
            mock_error.reset_mock()
            logger.critical("Critical message", exc_info=False)
            mock_error.assert_called_once_with("Critical message", exc_info=False)

    @patch.object(Settings, "headless_mode", False)
    def test_prompt_non_headless_with_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test prompt method in non-headless mode with _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        # Configure the mock prompt to return "y"
        mock_prompt_instance.ask.return_value = "y"

        result = logger.prompt("Choose option:", choices=["y", "n"], _default="n")
        assert result == "y"
        # Should NOT pass _default to underlying function (it's consumed by the wrapper)
        mock_prompt_instance.ask.assert_called_once_with(
            "Choose option:", choices=["y", "n"]
        )

    @patch.object(Settings, "headless_mode", False)
    def test_prompt_non_headless_without_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test prompt method in non-headless mode without _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        # Configure the mock prompt to return "y"
        mock_prompt_instance.ask.return_value = "y"

        result = logger.prompt("Choose option:", choices=["y", "n"])
        assert result == "y"
        # Should call without default parameter
        mock_prompt_instance.ask.assert_called_once_with(
            "Choose option:", choices=["y", "n"]
        )

    @patch.object(Settings, "headless_mode", True)
    def test_prompt_headless_with_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test prompt method in headless mode with _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        result = logger.prompt("Choose option:", choices=["y", "n"], _default="n")
        assert result == "n"
        # Should not call underlying function
        mock_prompt_instance.ask.assert_not_called()

    @patch.object(Settings, "headless_mode", True)
    def test_prompt_headless_without_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test prompt method in headless mode without _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        with pytest.raises(HeadlessPromptError):
            logger.prompt("Choose option:", choices=["y", "n"])
        mock_prompt_instance.ask.assert_not_called()

    @patch.object(Settings, "headless_mode", False)
    def test_confirm_non_headless_with_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test confirm method in non-headless mode with _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        # Configure the mock confirm to return True
        mock_confirm_instance.ask.return_value = True

        result = logger.confirm("Are you sure?", _default=False)
        assert result is True
        # Should NOT pass _default to underlying function (it's consumed by the wrapper)
        mock_confirm_instance.ask.assert_called_once_with("Are you sure?")

    @patch.object(Settings, "headless_mode", False)
    def test_confirm_non_headless_without_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test confirm method in non-headless mode without _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        # Configure the mock confirm to return True
        mock_confirm_instance.ask.return_value = True

        result = logger.confirm("Are you sure?")
        assert result is True
        # Should call without default parameter
        mock_confirm_instance.ask.assert_called_once_with("Are you sure?")

    @patch.object(Settings, "headless_mode", True)
    def test_confirm_headless_with_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test confirm method in headless mode with _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        result = logger.confirm("Are you sure?", _default=True)
        assert result is True
        # Should not call underlying function
        mock_confirm_instance.ask.assert_not_called()

    @patch.object(Settings, "headless_mode", True)
    def test_confirm_headless_without_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test confirm method in headless mode without _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        with pytest.raises(HeadlessPromptError):
            logger.confirm("Are you sure?")
        mock_confirm_instance.ask.assert_not_called()

    @patch.object(Settings, "headless_mode", False)
    def test_input_non_headless_without_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test input method in non-headless mode without _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        # Configure the mock console input to return "user_input"
        mock_console_instance.input.return_value = "user_input"

        result = logger.input("Enter value:")
        assert result == "user_input"
        # Should NOT pass default to console.input (it doesn't support it)
        mock_console_instance.input.assert_called_once_with("Enter value:")

    @patch.object(Settings, "headless_mode", False)
    def test_input_non_headless_with_default_ignored(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test input method in non-headless mode with _default parameter (should be ignored)."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        # Configure the mock console input to return "user_input"
        mock_console_instance.input.return_value = "user_input"

        result = logger.input("Enter value:", _default="default_value")
        assert result == "user_input"
        # Should NOT pass _default to console.input (it's consumed by the wrapper)
        mock_console_instance.input.assert_called_once_with("Enter value:")

    @patch.object(Settings, "headless_mode", True)
    def test_input_headless_with_default(self, mock_prompt, mock_confirm, mock_console):
        """Test input method in headless mode with _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        result = logger.input("Enter value:", _default="default_value")
        assert result == "default_value"
        # Should not call underlying function
        mock_console_instance.input.assert_not_called()

    @patch.object(Settings, "headless_mode", True)
    def test_input_headless_without_default(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test input method in headless mode without _default parameter."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        with pytest.raises(HeadlessPromptError):
            logger.input("Enter value:")
        mock_console_instance.input.assert_not_called()

    def test_reproduction_of_original_app_error(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test that the original error from app.py is now fixed."""
        # Set up mock instances
        mock_console_instance = MagicMock()
        mock_console_error_instance = MagicMock()
        mock_console.side_effect = [mock_console_instance, mock_console_error_instance]

        mock_confirm_instance = MagicMock()
        mock_confirm.return_value = mock_confirm_instance

        mock_prompt_instance = MagicMock()
        mock_prompt.return_value = mock_prompt_instance

        logger = Logger()

        with patch.object(Settings, "headless_mode", True):
            # This was the failing call from app.py - should now work
            result = logger.prompt("", choices=["y", "n", "skip"], _default="n")
            assert result == "n"

        with patch.object(Settings, "headless_mode", False):
            # Configure the mock prompt to return "y"
            mock_prompt_instance.ask.return_value = "y"

            result = logger.prompt("", choices=["y", "n", "skip"], _default="n")
            assert result == "y"
            # Should NOT pass _default to underlying function (it's consumed by the wrapper)
            mock_prompt_instance.ask.assert_called_once_with(
                "", choices=["y", "n", "skip"]
            )

    def test_headless_wrapper_functionality(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test headless wrapper directly."""
        mock_fn = Mock(return_value="result")
        wrapped_fn = Logger.headless_wrapper(mock_fn)

        # Test in non-headless mode with _default
        with patch.object(Settings, "headless_mode", False):
            result = wrapped_fn("arg1", _default="default_val", kwarg1="value1")
            assert result == "result"
            mock_fn.assert_called_once_with("arg1", kwarg1="value1")

        # Test in headless mode with _default
        mock_fn.reset_mock()
        with patch.object(Settings, "headless_mode", True):
            result = wrapped_fn("arg1", _default="default_val", kwarg1="value1")
            assert result == "default_val"
            mock_fn.assert_not_called()

        # Test in headless mode without _default (should raise error)
        with patch.object(Settings, "headless_mode", True):
            with pytest.raises(HeadlessPromptError):
                wrapped_fn("arg1", kwarg1="value1")

    @patch.object(Settings, "headless_mode", False)
    def test_print_property_non_headless(self, mock_prompt, mock_confirm, mock_console):
        """Test print property in non-headless mode."""
        logger = Logger()

        # Should return console.print
        assert logger.print == logger.console.print

    @patch.object(Settings, "headless_mode", True)
    def test_print_property_headless(self, mock_prompt, mock_confirm, mock_console):
        """Test print property in headless mode."""
        logger = Logger()

        # Should return a no-op function
        print_func = logger.print
        assert callable(print_func)

        # Calling it should not raise an error and should return None
        result = print_func("test message")
        assert result is None

    def test_get_instance_creates_new_logger(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test get_instance creates a new logger when none exists."""
        assert Logger._instance is None

        logger = Logger.get_instance()
        assert isinstance(logger, Logger)
        assert logger.name == "Pieces_CLI"

    def test_get_instance_returns_existing_instance(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test get_instance returns existing instance when available."""
        # Create an instance manually
        Logger._instance = Logger(debug_mode=True)

        # Get instance should return the existing one
        logger = Logger.get_instance()
        assert logger is Logger._instance
        assert logger.debug_mode is True

    def test_handler_cleanup_on_init(self, mock_prompt, mock_confirm, mock_console):
        """Test that existing handlers are removed on initialization."""
        logger = Logger()

        # Add a handler manually
        test_handler = logging.StreamHandler()
        logger.logger.addHandler(test_handler)
        assert test_handler in logger.logger.handlers

        # Create new logger instance - should clean up handlers
        new_logger = Logger()
        assert test_handler not in new_logger.logger.handlers

    def test_file_logging_integration(self, mock_prompt, mock_confirm, mock_console):
        """Test complete file logging integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = Logger(debug_mode=True, log_dir=temp_dir)

            # Log some messages
            logger.info("Test info message")
            logger.error("Test error message")
            logger.debug("Test debug message")

            # Flush the handler to ensure messages are written
            if hasattr(logger, "file_handler"):
                logger.file_handler.flush()

            # Check that log file contains messages
            log_files = list(Path(temp_dir, "logs").glob("*.log"))
            assert len(log_files) > 0

            log_content = log_files[0].read_text()
            assert "Test info message" in log_content
            assert "Test error message" in log_content
            assert "Test debug message" in log_content

    def test_log_level_filtering(self, mock_prompt, mock_confirm, mock_console):
        """Test that log level filtering works correctly."""
        # Test with debug mode off (ERROR level)
        logger_error = Logger(debug_mode=False)
        assert logger_error.logger.level == logging.ERROR

        # Test with debug mode on (DEBUG level)
        logger_debug = Logger(debug_mode=True)
        assert logger_debug.logger.level == logging.DEBUG

    @patch.object(Settings, "headless_mode", False)
    def test_rich_components_initialization(
        self, mock_prompt, mock_confirm, mock_console
    ):
        """Test that Rich components are properly initialized."""
        logger = Logger()

        # Check that Rich components exist
        assert logger.console is not None
        assert logger.console_error is not None
        assert logger._confirm is not None
        assert logger._prompt is not None

        # Check that wrapped methods are callable
        assert callable(logger.confirm)
        assert callable(logger.prompt)
        assert callable(logger.input)
