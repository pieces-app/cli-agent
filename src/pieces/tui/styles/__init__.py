"""Styles module for TUI application with Textual best practices."""

from pathlib import Path


def get_styles_dir() -> Path:
    """Get the path to the styles directory."""
    return Path(__file__).parent


def load_css_file(filename: str) -> str:
    """Load a CSS file from the styles directory."""
    css_path = get_styles_dir() / filename
    if css_path.exists():
        return css_path.read_text(encoding='utf-8')
    return ""


def load_all_styles() -> str:
    """Load and combine all TCSS files in order."""
    css_files = [
        "base.tcss",
        "colors.tcss", 
        "animations.tcss",
        "conversations.tcss",
        "chat.tcss",  # Now includes input styles
    ]

    combined_css = []
    for filename in css_files:
        css_content = load_css_file(filename)
        if css_content:
            combined_css.append(f"/* {filename} */")
            combined_css.append(css_content)
            combined_css.append("")
    return "\n".join(combined_css)


# Single source of truth for CSS
FULL_CSS = load_all_styles()

__all__ = [
    "FULL_CSS",
    "load_css_file", 
    "load_all_styles",
    "get_styles_dir",
]

