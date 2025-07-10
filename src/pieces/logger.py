import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Self, Any

from rich import prompt
from rich.console import Console
from rich.prompt import Prompt

from pieces.headless.exceptions import HeadlessPromptError


class Logger:
    _instance: Optional[Self] = None

    def __init__(self, debug_mode=False, log_dir=None):
        """
        Initialize the logger.

        Args:
            debug_mode (bool): Whether to enable debug output
            log_dir (str, optional): Directory to store log files (only used in debug mode)
        """
        self.name = "Pieces_CLI"
        self.console = Console()
        self.console_error = Console(stderr=True)
        self._confirm = prompt.Confirm(console=self.console)
        self._prompt = Prompt(console=self.console)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.CRITICAL)

        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        self.debug_mode = debug_mode
        if debug_mode and log_dir:
            self._setup_file_logging(os.path.join(log_dir, "logs"), self.name)
            # self.print("Running in debug mode") Sadly it leads to some issues wit the claude MCP

    def _setup_file_logging(self, log_dir, name):
        """Set up file logging to save logs to files."""
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Create log file with timestamp
        timestamp = datetime.today().strftime("%Y%m%d")
        log_file = log_path / f"{name}_{timestamp}.log"

        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)
        self.file_handler = file_handler

    def info(self, message, *args, **kwargs):
        """Log an info message."""
        self.logger.info(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        """Log an error message."""
        exc_info = kwargs.pop("exc_info", True)
        self.logger.error(message, exc_info=exc_info, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """Log a debug message (only visible in debug mode)."""
        self.logger.debug(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        """Log a critical message."""
        exc_info = kwargs.pop("exc_info", True)
        self.logger.error(message, exc_info=exc_info, *args, **kwargs)

    @property
    def input(self):
        """Get user input with a prompt."""
        if not self._is_headless_mode():
            return self.console.input
        raise HeadlessPromptError()

    @property
    def print(self):
        if not self._is_headless_mode():
            return self.console.print
        return lambda *args, **kwargs: None

    def handle_input(self, default: Optional[str] = None, *args, **kwargs) -> str:
        """Handle user input with an optional default value."""
        if default:
            return default
        raise HeadlessPromptError()

    @property
    def prompt(self):
        if not self._is_headless_mode():
            return self._prompt.ask
        return self.handle_input

    @property
    def confirm(self):
        if not self._is_headless_mode():
            return self._confirm.ask
        return self.handle_input

    def _is_headless_mode(self) -> bool:
        """Check if currently in headless mode."""
        from pieces.settings import Settings

        return Settings.headless_mode

    @classmethod
    def get_instance(cls):
        return cls._instance or Logger()
