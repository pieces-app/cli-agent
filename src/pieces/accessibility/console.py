"""
Accessible console wrapper for Rich Console.

Provides accessibility-aware console output that respects:
- NO_COLOR environment variable
- Color scheme preferences
- Screen reader compatibility
- Verbose/descriptive output modes
"""

from typing import Any, Optional
from rich.console import Console
from rich.text import Text

from pieces.accessibility.config import AccessibilityConfig


class AccessibleConsole:
    """
    Accessible wrapper around Rich Console.
    
    Automatically applies accessibility preferences to all console output.
    """
    
    def __init__(self, config: Optional[AccessibilityConfig] = None, **console_kwargs):
        """
        Initialize accessible console.
        
        Args:
            config: AccessibilityConfig instance (creates default if None)
            **console_kwargs: Arguments to pass to Rich Console
        """
        self._config = config or AccessibilityConfig()
        
        # Force no colors if NO_COLOR is set
        if self._config.no_color:
            console_kwargs['no_color'] = True
        
        self._console = Console(**console_kwargs)
    
    @property
    def config(self) -> AccessibilityConfig:
        """Get the accessibility configuration."""
        return self._config
    
    @property
    def console(self) -> Console:
        """Get the underlying Rich Console."""
        return self._console
    
    def print(self, *args, **kwargs) -> None:
        """
        Print to console with accessibility-aware formatting.
        
        Automatically applies color scheme preferences, text indicators,
        and screen reader friendly formatting.
        """
        # Process args to add accessibility indicators
        processed_args = []
        for arg in args:
            processed_args.append(self._format_accessible(arg))
        
        # For screen readers, add a newline separator for better parsing
        if self._config.screen_reader:
            self._console.print(*processed_args, **kwargs)
            # Add extra spacing for screen reader clarity
            if len(processed_args) > 0:
                self._console.print()  # Blank line for separation
        else:
            self._console.print(*processed_args, **kwargs)
    
    def _format_accessible(self, content: Any) -> Any:
        """
        Format content for accessibility.
        
        Args:
            content: Content to format
            
        Returns:
            Formatted content with accessibility considerations
        """
        if isinstance(content, str):
            return self._format_string_accessible(content)
        elif isinstance(content, Text):
            return self._format_text_accessible(content)
        return content
    
    def _format_string_accessible(self, text: str) -> str:
        """
        Format string with accessibility indicators.
        
        Detects Rich markup patterns and adds text indicators when colors are disabled.
        For screen readers, adds descriptive prefixes and removes visual-only formatting.
        """
        import re
        
        # Handle screen reader mode
        if self._config.screen_reader:
            return self._format_for_screen_reader(text)
        
        # Handle NO_COLOR mode
        if not self._config.no_color:
            return text
        
        # Add text indicators for common Rich color patterns
        # [red]Error[/red] -> ✗ Error
        # [green]Success[/green] -> ✓ Success
        # [yellow]Warning[/yellow] -> ⚠ Warning
        
        # Pattern to match [color]text[/color]
        color_pattern = r'\[(red|green|yellow|blue|bright_red|bright_green|bright_yellow)\](.*?)\[/\1\]'
        
        def add_indicator(match):
            color = match.group(1)
            content = match.group(2)
            
            # Map Rich colors to semantic colors
            color_map = {
                'red': 'error',
                'green': 'success',
                'yellow': 'warning',
                'blue': 'info',
                'bright_red': 'error',
                'bright_green': 'success',
                'bright_yellow': 'warning'
            }
            
            semantic = color_map.get(color, 'info')
            indicator = self._config.get_text_indicator(semantic)
            
            if indicator:
                return f"{indicator} {content}"
            return content
        
        return re.sub(color_pattern, add_indicator, text, flags=re.IGNORECASE)
    
    def _format_for_screen_reader(self, text: str) -> str:
        """
        Format text specifically for screen readers.
        
        Removes visual-only formatting and adds descriptive prefixes.
        """
        import re
        
        # Remove Rich markup tags
        text = re.sub(r'\[/?[^\]]+\]', '', text)
        
        # Remove common visual indicators that might confuse screen readers
        # Keep semantically meaningful Unicode characters
        visual_indicators = [
            r'[─━│┃┌┐└┘├┤┬┴┼╋╌╍┄┅┆┇]',  # Box drawing characters
            r'[░▒▓█]',  # Block characters
            r'[◇◆○●□■]',  # Geometric shapes
        ]
        
        for pattern in visual_indicators:
            text = re.sub(pattern, '', text)
        
        # Replace multiple spaces with single space for better speech
        text = re.sub(r'\s+', ' ', text)
        
        # Add descriptive prefix if this looks like a message
        # Try to detect message type from context
        message_patterns = {
            r'(?i)error': 'Error: ',
            r'(?i)warning': 'Warning: ',
            r'(?i)success': 'Success: ',
            r'(?i)info': 'Information: ',
        }
        
        for pattern, prefix in message_patterns.items():
            if re.search(pattern, text):
                if not text.startswith(prefix.strip()):
                    text = prefix + text
                break
        
        return text.strip()
    
    def _format_text_accessible(self, text: Text) -> Text:
        """
        Format Rich Text object for accessibility.
        """
        # For screen readers, use plain text without styling
        if self._config.screen_reader:
            accessible_text = Text(text.plain)
            return accessible_text
        
        if not self._config.no_color:
            return text
        
        # Remove styling when NO_COLOR is set
        accessible_text = Text(text.plain)
        return accessible_text
    
    def __getattr__(self, name: str) -> Any:
        """
        Delegate any other methods to the underlying Rich Console.
        """
        return getattr(self._console, name)
    
    def __enter__(self):
        """Context manager support."""
        return self._console.__enter__()
    
    def __exit__(self, *args):
        """Context manager support."""
        return self._console.__exit__(*args)
    
    def print_structure(self, title: str, items: list, **kwargs) -> None:
        """
        Print structured data in a screen reader friendly format.
        
        Args:
            title: Title/heading for the structure
            items: List of items to display
            **kwargs: Additional arguments for Rich Console
        """
        if self._config.screen_reader:
            # Screen reader friendly format
            self._console.print(f"=== {title} ===")
            for i, item in enumerate(items, 1):
                self._console.print(f"{i}. {item}")
            self._console.print()  # Blank line for separation
        else:
            # Standard Rich formatting
            self._console.print(f"[bold]{title}[/bold]")
            for item in items:
                self._console.print(f"  • {item}")
    
    def print_progress(self, message: str, current: int, total: int, **kwargs) -> None:
        """
        Print progress information in a screen reader friendly format.
        
        Args:
            message: Progress message
            current: Current progress value
            total: Total progress value
            **kwargs: Additional arguments for Rich Console
        """
        if self._config.screen_reader:
            # Screen reader friendly: speak the percentage
            percentage = (current / total) * 100 if total > 0 else 0
            self._console.print(f"{message}: {current} of {total} ({percentage:.0f} percent)")
        else:
            # Standard Rich formatting
            self._console.print(f"{message}: {current}/{total}", **kwargs)
    
    def print_list(self, items: list, title: str = "", **kwargs) -> None:
        """
        Print a list in a screen reader friendly format.
        
        Args:
            items: List of items to display
            title: Optional title for the list
            **kwargs: Additional arguments for Rich Console
        """
        if self._config.screen_reader:
            if title:
                self._console.print(f"List: {title}")
            for i, item in enumerate(items, 1):
                self._console.print(f"Item {i}: {item}")
            self._console.print()  # Blank line for separation
        else:
            if title:
                self._console.print(f"[bold]{title}[/bold]")
            for item in items:
                self._console.print(f"  • {item}", **kwargs)