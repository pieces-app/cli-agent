import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Self

from rich import prompt
from rich.console import Console
from rich.prompt import Prompt


class Logger:
    _instance: Self

    def __init__(self, debug_mode=False, log_dir=None):
        """
        Initialize the logger.

        Args:
            debug_mode (bool): Whether to enable debug output
            log_dir (str, optional): Directory to store log files (only used in debug mode)
        """
        Logger._instance = self
        self.name = "Pieces_CLI"
        self.console = Console()
        self._confirm = prompt.Confirm(console=self.console)
        self._prompt = Prompt(console=self.console)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.CRITICAL)

        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        self.debug_mode = debug_mode
        if debug_mode:
            log_dir = log_dir or os.path.join(os.getcwd(), "logs")
            self._setup_file_logging(log_dir, self.name)
            self.print("Running in debug mode")

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
        return self.console.input

    @property
    def print(self):
        return self.console.print

    @property
    def prompt(self):
        return self._prompt.ask

    @property
    def confirm(self):
        return self._confirm.ask

    @classmethod
    def get_instance(cls):
        return cls._instance or Logger()
