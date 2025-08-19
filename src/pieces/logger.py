import logging
import os
import sys
from datetime import datetime
import sentry_sdk
from pathlib import Path
from typing import Optional, Self, Any, Callable
from functools import wraps

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
        Logger._instance = self
        self.name = "Pieces_CLI"
        self.console = Console()
        self.console_error = Console(stderr=True)
        self._confirm = prompt.Confirm(console=self.console)
        self._prompt = Prompt(console=self.console)

        # Wrap the ask methods with proper typing
        self.confirm: Callable[..., bool] = self.headless_wrapper(self._confirm.ask)
        self.prompt: Callable[..., str] = self.headless_wrapper(self._prompt.ask)
        self.input: Callable[..., str] = self.headless_wrapper(self.console.input)

        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG if debug_mode else logging.ERROR)

        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        self.debug_mode = debug_mode
        if log_dir:
            self._setup_file_logging(os.path.join(log_dir, "logs"), self.name)

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

    def warning(self, message, *args, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, ignore_sentry=False, **kwargs):
        """Log an error message."""
        exc_info = kwargs.pop("exc_info", True)
        _, exc_value, _ = sys.exc_info()
        if exc_value is not None and not ignore_sentry:
            sentry_sdk.capture_exception(exc_value)
        self.logger.error(message, exc_info=exc_info, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        """Log a debug message (only visible in debug mode)."""
        self.logger.debug(message, *args, **kwargs)

    def critical(self, message, *args, ignore_sentry=False, **kwargs):
        """Log a critical message."""
        exc_info = kwargs.pop("exc_info", True)
        _, exc_value, _ = sys.exc_info()
        if exc_value is not None and not ignore_sentry:
            sentry_sdk.capture_exception(exc_value)
        self.logger.error(message, exc_info=exc_info, *args, **kwargs)

    @staticmethod
    def headless_wrapper(ask_fn: Callable) -> Callable[..., Any]:
        """Wrap a Rich ask function to support headless mode with optional default fallback."""

        @wraps(ask_fn)
        def wrapper(*args, _default: Optional[Any] = None, **kwargs) -> Any:
            from pieces.settings import Settings

            if Settings.headless_mode:
                if _default is not None:
                    return _default
                raise HeadlessPromptError(
                    f"{getattr(ask_fn, __name__, ask_fn)}({kwargs=}, {args=})"
                )

            return ask_fn(*args, **kwargs)

        return wrapper

    @property
    def print(self):
        from pieces.settings import Settings

        if not Settings.headless_mode:
            return self.console.print
        return lambda *args, **kwargs: None

    @classmethod
    def get_instance(cls):
        return cls._instance or Logger()
