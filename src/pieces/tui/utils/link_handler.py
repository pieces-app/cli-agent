"""Utility class for handling markdown file links in Textual widgets."""

import os
import re
import sys
import subprocess
import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING, Set

if TYPE_CHECKING:
    from textual.widgets import Markdown

from pieces.settings import Settings


class LinkHandler:
    """Utility class for processing and handling markdown links."""

    # Whitelist of safe file extensions that can be opened
    SAFE_FILE_EXTENSIONS: Set[str] = {
        ".txt",
        ".md",
        ".py",
        ".js",
        ".html",
        ".css",
        ".json",
        ".xml",
        ".yaml",
        ".yml",
        ".log",
        ".csv",
        ".sql",
        ".sh",
        ".bash",
        ".conf",
        ".ini",
        ".cfg",
        ".toml",
        ".rst",
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".bmp",
        ".ico",
        ".mp4",
        ".mp3",
        ".wav",
        ".avi",
        ".mov",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".zip",
        ".tar",
        ".gz",
        ".7z",
        ".rar",
    }

    # Maximum allowed file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    @staticmethod
    def process_file_links(content: str) -> str:
        """Convert file:// protocol links to proper relative paths for Textual."""
        # Pattern to match [text](file://path) links
        pattern = r"\[([^\]]+)\]\(file://([^)]+)\)"

        def replace_file_link(match):
            link_text = match.group(1)
            file_path = match.group(2)

            # Convert to relative path format that Textual can handle
            if file_path.startswith("/"):
                # For absolute paths, try to make them relative to current directory
                try:
                    current_dir = os.getcwd()
                    if file_path.startswith(current_dir):
                        file_path = os.path.relpath(file_path, current_dir)
                    # Keep as absolute path but remove file:// protocol for other cases
                except Exception:
                    # Fallback: just remove file:// and keep the path
                    pass

            # Return proper markdown link format
            return f"[{link_text}]({file_path})"

        return re.sub(pattern, replace_file_link, content)

    @staticmethod
    async def handle_link_click(event: "Markdown.LinkClicked", app=None) -> None:
        """Handle clicks on markdown links."""
        Settings.logger.info(f"Link clicked: {event.href}")

        # Check if it's a file path
        if not event.href.startswith(("http://", "https://")):
            await LinkHandler._handle_file_link(event.href, app)
        else:
            LinkHandler._handle_web_link(event.href)

    @staticmethod
    def _is_safe_file(file_path: str) -> bool:
        """Check if a file is safe to open based on extension and other criteria."""
        try:
            path = Path(file_path)

            # Check file extension
            if path.suffix.lower() not in LinkHandler.SAFE_FILE_EXTENSIONS:
                return False

            # Check if file exists and get its size
            if not path.exists():
                return True  # Let the system handle non-existent files

            # Check file size (avoid opening very large files)
            if path.stat().st_size > LinkHandler.MAX_FILE_SIZE:
                return False

            # Additional security checks
            resolved_path = path.resolve()

            # Prevent access to system directories (basic protection)
            system_dirs = [
                "/bin",
                "/sbin",
                "/usr/bin",
                "/usr/sbin",
                "/etc",
                "/var",
                "/sys",
                "/proc",
            ]
            if sys.platform != "win32":
                for sys_dir in system_dirs:
                    if str(resolved_path).startswith(sys_dir):
                        return False

            return True

        except Exception:
            # If we can't validate the file, consider it unsafe
            return False

    @staticmethod
    def _validate_path(file_path: str) -> str:
        """Validate and sanitize a file path."""
        try:
            # Resolve the path to prevent path traversal
            resolved = Path(file_path).resolve()

            # Convert back to string
            return str(resolved)

        except Exception as e:
            Settings.logger.error(f"Path validation failed for {file_path}: {e}")
            raise ValueError(f"Invalid file path: {file_path}")

    @staticmethod
    async def _handle_file_link(file_path: str, app=None) -> None:
        """Handle file path links with security validation."""
        try:
            # Validate and resolve the path
            validated_path = LinkHandler._validate_path(file_path)

            # Check if file exists
            if not os.path.exists(validated_path):
                Settings.logger.warning(f"File not found: {validated_path}")
                return

            # Check if file is safe
            if LinkHandler._is_safe_file(validated_path):
                # Safe file - open directly
                LinkHandler._open_file_safely(validated_path)
            else:
                # Unsafe file - show security warning dialog
                await LinkHandler._show_security_warning_and_open(validated_path, app)

        except ValueError as e:
            Settings.logger.error(f"Invalid file path: {e}")
        except Exception as e:
            Settings.logger.error(f"Failed to handle file link {file_path}: {e}")

    @staticmethod
    def _open_file_safely(file_path: str) -> None:
        """Open a file using the system default application."""
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", file_path], check=False)
            else:  # Linux and others
                subprocess.run(["xdg-open", file_path], check=False)

            Settings.logger.info(f"Opened file: {file_path}")
        except Exception as e:
            Settings.logger.error(f"Failed to open file {file_path}: {e}")

    @staticmethod
    async def _show_security_warning_and_open(file_path: str, app=None) -> None:
        """Show security warning dialog for potentially unsafe files."""
        try:
            from pieces.tui.widgets.dialogs import ConfirmDialog

            if app:
                file_name = Path(file_path).name
                file_ext = Path(file_path).suffix

                # Create a more detailed warning message
                risk_details = LinkHandler._get_risk_details(file_ext)
                warning_message = f"""The file '{file_name}' may be potentially unsafe to open!

{risk_details}

Are you sure you want to open this file?"""

                dialog = ConfirmDialog(
                    title="⚠️ Security Warning",
                    message=warning_message,
                    width=70,
                    height=16,
                )

                result = await app.push_screen_wait(dialog)
                if result:  # User confirmed they want to open the file
                    LinkHandler._open_file_safely(file_path)
                    Settings.logger.info(
                        f"User confirmed opening potentially unsafe file: {file_path}"
                    )
                else:
                    Settings.logger.info(
                        f"User cancelled opening potentially unsafe file: {file_path}"
                    )
            else:
                # Fallback if app not available - log warning and don't open
                Settings.logger.warning(
                    f"Cannot open potentially unsafe file (no app available): {file_path}"
                )
        except ImportError:
            # Fallback if dialog not available - log warning and don't open
            Settings.logger.warning(
                f"Cannot open potentially unsafe file (no dialog available): {file_path}"
            )
        except Exception as e:
            Settings.logger.error(f"Error showing security warning: {e}")

    @staticmethod
    def _get_risk_details(file_extension: str) -> str:
        """Get risk details based on file extension."""
        risk_map = {
            ".exe": "• Executable files can run malicious code\n• May contain viruses or malware",
            ".bat": "• Batch scripts can execute system commands\n• May modify or delete files",
            ".sh": "• Shell scripts can execute system commands\n• May access sensitive system areas",
            ".ps1": "• PowerShell scripts have system access\n• Can modify registry and system settings",
            ".app": "• Application bundles can contain malware\n• May request system permissions",
            ".dmg": "• Disk images may contain malicious software\n• Could install unwanted programs",
            ".msi": "• Installer packages can modify system\n• May install malware or unwanted software",
        }

        ext_lower = file_extension.lower()
        if ext_lower in risk_map:
            return risk_map[ext_lower]

        # Generic warning for unknown extensions
        return f"• Files with '{file_extension}' extension may pose risks\n• Unknown file types should be treated with caution\n• Large files may consume significant system resources"

    @staticmethod
    def _handle_web_link(url: str) -> None:
        """Handle web URL links."""
        try:
            webbrowser.open(url)
            Settings.logger.info(f"Opened URL: {url}")
        except Exception as e:
            Settings.logger.error(f"Failed to open URL {url}: {e}")
