"""
Base manager class for configuration management.

Provides common functionality to avoid code duplication.
"""

import json
import threading
import contextlib
import sys
from pathlib import Path
from typing import Optional, TypeVar, Type, Generic
from abc import ABC
from pydantic import BaseModel


T = TypeVar("T", bound=BaseModel)

# Global lock registry to avoid concurrent writes to the same config file
_CONFIG_LOCKS: dict[Path, threading.Lock] = {}


def _get_lock(path: Path) -> threading.Lock:
    """Get a threading lock for a given file path (singleton per-path)."""
    lock = _CONFIG_LOCKS.get(path)
    if lock is None:
        lock = threading.Lock()
        _CONFIG_LOCKS[path] = lock
    return lock


@contextlib.contextmanager
def _file_lock(path: Path):
    """Context manager that acquires an OS-level exclusive lock on *path*."""

    if sys.platform == "win32":
        # On Windows, use a lock file approach to avoid file handle conflicts
        lock_file = path.with_suffix(path.suffix + ".lock")
        import msvcrt

        try:
            # Create and lock a separate lock file
            with open(lock_file, "w") as _fh:
                fd = _fh.fileno()
                try:
                    msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
                    yield
                finally:
                    try:
                        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                    except OSError:
                        pass
            # Clean up lock file
            try:
                lock_file.unlink(missing_ok=True)
            except OSError:
                pass
        except (FileNotFoundError, PermissionError, OSError):
            # Fallback: if locking fails, just proceed without OS-level lock
            # The threading lock should provide basic protection
            yield
    else:
        import fcntl

        with open(path, "a") as _fh:
            try:
                fcntl.flock(_fh.fileno(), fcntl.LOCK_EX)
                yield
            finally:
                try:
                    fcntl.flock(_fh.fileno(), fcntl.LOCK_UN)
                except OSError:
                    pass


class BaseConfigManager(Generic[T], ABC):
    """Base class for configuration managers."""

    def __init__(self, config_path: Path, schema_class: Type[T]):
        """
        Initialize base manager.

        Args:
            config_path: Full path to the configuration file
            schema_class: Pydantic schema class for this config type
        """
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.schema_class = schema_class
        self._config: Optional[T] = None

    def _get_file_path(self) -> Path:
        """Get file path for this configuration."""
        return self.config_path

    @property
    def config(self) -> T:
        """Get current configuration (lazy loaded)."""
        if self._config is None:
            self._config = self._load_or_create()
        return self._config

    def _load_or_create(self) -> T:
        """Load configuration or create default."""
        file_path = self._get_file_path()
        lock = _get_lock(file_path)

        if not file_path.exists():
            config = self.schema_class()
            self._save_config(config)
            return config

        try:
            with (
                lock,
                _file_lock(file_path),
                open(file_path, "r", encoding="utf-8") as f,
            ):
                data = json.load(f)
            # Pydantic validates automatically
            return self.schema_class(**data)
        except (json.JSONDecodeError, Exception) as e:
            # Lazy import to avoid circular dependency
            from ...settings import Settings  # type: ignore

            Settings.logger.error(f"Failed to load config '{self.config_path}': {e}")
            # Return default config
            config = self.schema_class()
            self._save_config(config)
            return config

    def _save_config(self, config: BaseModel) -> bool:
        """Save configuration to file."""
        file_path = self._get_file_path()
        lock = _get_lock(file_path)
        try:
            with (
                lock,
                _file_lock(file_path),
                open(file_path, "w", encoding="utf-8") as f,
            ):
                json.dump(config.model_dump(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            from ...settings import Settings  # type: ignore

            Settings.logger.error(f"Failed to save config '{self.config_path}': {e}")
            return False

    def reload(self) -> None:
        """Reload configuration from file."""
        self._config = self._load_or_create()

    def save(self) -> bool:
        """Save current configuration."""
        if self._config is None:
            return False
        return self._save_config(self._config)

    def reset_to_defaults(self) -> bool:
        """Reset configuration to default values."""
        self._config = self.schema_class()
        return self.save()

    def exists(self) -> bool:
        """Check if configuration file exists."""
        return self._get_file_path().exists()

    def delete(self) -> bool:
        """Delete configuration file."""
        file_path = self._get_file_path()
        lock = _get_lock(file_path)
        try:
            with lock, _file_lock(file_path):
                if file_path.exists():
                    file_path.unlink()
            self._config = None
            return True
        except Exception as e:
            from ...settings import Settings  # type: ignore

            Settings.logger.error(f"Failed to delete config '{self.config_path}': {e}")
            return False
