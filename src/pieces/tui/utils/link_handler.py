"""Utility class for handling markdown file links in Textual widgets."""

import os
import re
import sys
import subprocess
import webbrowser
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from textual.widgets import Markdown

from pieces.settings import Settings


class LinkHandler:
    """Utility class for processing and handling markdown links."""

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
    async def handle_link_click(event: "Markdown.LinkClicked") -> None:
        """Handle clicks on markdown links."""
        Settings.logger.info(f"Link clicked: {event.href}")

        # Check if it's a file path
        if not event.href.startswith(("http://", "https://")):
            LinkHandler._handle_file_link(event.href)
        else:
            LinkHandler._handle_web_link(event.href)

    @staticmethod
    def _handle_file_link(file_path: str) -> None:
        """Handle file path links."""
        # Convert to absolute path if relative
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(file_path)

        # Check if file exists
        if os.path.exists(file_path):
            try:
                # Open file with system default application
                if sys.platform == "win32":
                    os.startfile(file_path)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", file_path])
                else:  # Linux and others
                    subprocess.run(["xdg-open", file_path])

                Settings.logger.info(f"Opened file: {file_path}")
            except Exception as e:
                Settings.logger.error(f"Failed to open file {file_path}: {e}")
        else:
            Settings.logger.warning(f"File not found: {file_path}")

    @staticmethod
    def _handle_web_link(url: str) -> None:
        """Handle web URL links."""
        try:
            webbrowser.open(url)
            Settings.logger.info(f"Opened URL: {url}")
        except Exception as e:
            Settings.logger.error(f"Failed to open URL {url}: {e}")
