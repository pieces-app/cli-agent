"""
Keyboard navigation helpers for Pieces CLI.

Provides utilities for enhanced keyboard navigation and accessibility including:
- Keyboard shortcut management
- Menu navigation aids
- Reduced motion animations
- Focus management
"""

from typing import Optional, Dict, List, Callable
from dataclasses import dataclass


@dataclass
class KeyboardShortcut:
    """Represents a keyboard shortcut."""
    key: str
    description: str
    action: Callable
    category: str = "general"


class KeyboardNavigation:
    """
    Manages keyboard navigation and shortcuts for accessibility.
    
    Provides enhanced keyboard navigation features for users who prefer
    keyboard-only interaction or require keyboard accessibility.
    """
    
    def __init__(self, keyboard_nav_enabled: bool = False, reduced_motion: bool = False):
        """
        Initialize keyboard navigation manager.
        
        Args:
            keyboard_nav_enabled: Whether keyboard navigation mode is enabled
            reduced_motion: Whether reduced motion mode is enabled
        """
        self._keyboard_nav_enabled = keyboard_nav_enabled
        self._reduced_motion = reduced_motion
        self._shortcuts: Dict[str, KeyboardShortcut] = {}
        self._default_shortcuts()
    
    @property
    def keyboard_nav_enabled(self) -> bool:
        """Check if keyboard navigation is enabled."""
        return self._keyboard_nav_enabled
    
    @property
    def reduced_motion(self) -> bool:
        """Check if reduced motion is enabled."""
        return self._reduced_motion
    
    def _default_shortcuts(self):
        """Register default keyboard shortcuts."""
        # Common navigation shortcuts
        self.register_shortcut(
            KeyboardShortcut(
                key="q",
                description="Quit/Exit",
                action=lambda: None,  # Placeholder for quit action
                category="navigation"
            )
        )
        self.register_shortcut(
            KeyboardShortcut(
                key="?",
                description="Show help",
                action=lambda: None,  # Placeholder for help action
                category="help"
            )
        )
        self.register_shortcut(
            KeyboardShortcut(
                key="h",
                description="Go to home",
                action=lambda: None,  # Placeholder for home action
                category="navigation"
            )
        )
    
    def register_shortcut(self, shortcut: KeyboardShortcut) -> None:
        """
        Register a keyboard shortcut.
        
        Args:
            shortcut: KeyboardShortcut to register
        """
        self._shortcuts[shortcut.key] = shortcut
    
    def get_shortcut(self, key: str) -> Optional[KeyboardShortcut]:
        """
        Get a keyboard shortcut by key.
        
        Args:
            key: Shortcut key
            
        Returns:
            KeyboardShortcut if found, None otherwise
        """
        return self._shortcuts.get(key)
    
    def get_shortcuts_by_category(self, category: str) -> List[KeyboardShortcut]:
        """
        Get all shortcuts in a category.
        
        Args:
            category: Category name
            
        Returns:
            List of KeyboardShortcut objects
        """
        return [s for s in self._shortcuts.values() if s.category == category]
    
    def get_all_shortcuts(self) -> List[KeyboardShortcut]:
        """
        Get all registered shortcuts.
        
        Returns:
            List of all KeyboardShortcut objects
        """
        return list(self._shortcuts.values())
    
    def format_shortcut_help(self) -> str:
        """
        Format keyboard shortcuts for display.
        
        Returns:
            Formatted string showing all shortcuts
        """
        if not self._keyboard_nav_enabled:
            return ""
        
        lines = ["Keyboard Shortcuts:", "=" * 20]
        
        # Group by category
        categories = {}
        for shortcut in self._shortcuts.values():
            if shortcut.category not in categories:
                categories[shortcut.category] = []
            categories[shortcut.category].append(shortcut)
        
        for category, shortcuts in sorted(categories.items()):
            lines.append(f"\n{category.capitalize()}:")
            for shortcut in shortcuts:
                lines.append(f"  {shortcut.key}: {shortcut.description}")
        
        return "\n".join(lines)
    
    def should_animate(self) -> bool:
        """
        Determine if animations should be shown.
        
        Returns:
            True if animations should be shown, False if reduced motion is enabled
        """
        return not self._reduced_motion
    
    def get_animation_delay(self, default_delay: float = 0.1) -> float:
        """
        Get animation delay based on reduced motion preference.
        
        Args:
            default_delay: Default animation delay in seconds
            
        Returns:
            Animation delay (0 if reduced motion is enabled)
        """
        if self._reduced_motion:
            return 0.0
        return default_delay
    
    def create_menu(self, items: List[str], title: str = "") -> str:
        """
        Create a keyboard-friendly menu representation.
        
        Args:
            items: List of menu items
            title: Optional menu title
            
        Returns:
            Formatted menu string with keyboard shortcuts
        """
        if not self._keyboard_nav_enabled:
            # Simple format when keyboard nav is disabled
            lines = []
            if title:
                lines.append(f"{title}:")
            for i, item in enumerate(items, 1):
                lines.append(f"  {i}. {item}")
            return "\n".join(lines)
        
        # Keyboard-friendly format with shortcuts
        lines = []
        if title:
            lines.append(f"{title} (Use number keys to select):")
        else:
            lines.append("Menu (Use number keys to select):")
        
        for i, item in enumerate(items, 1):
            # Assign keyboard shortcuts (1-9, then a-z)
            if i <= 9:
                key = str(i)
            else:
                key = chr(ord('a') + i - 10)
            
            lines.append(f"  [{key}] {item}")
        
        lines.append("\nPress [q] to quit, [?] for help")
        return "\n".join(lines)
    
    def create_progress_bar(self, current: int, total: int, width: int = 40) -> str:
        """
        Create a progress bar that respects reduced motion.
        
        Args:
            current: Current progress value
            total: Total progress value
            width: Width of the progress bar
            
        Returns:
            Formatted progress bar string
        """
        if total == 0:
            return "Progress: 0%"
        
        percentage = (current / total) * 100
        
        if self._reduced_motion:
            # Simple text format for reduced motion
            return f"Progress: {current}/{total} ({percentage:.0f}%)"
        
        # Visual progress bar
        filled = int(width * percentage / 100)
        bar = "█" * filled + "░" * (width - filled)
        return f"[{bar}] {percentage:.0f}% ({current}/{total})"
    
    def format_list_item(self, item: str, index: int, total: int) -> str:
        """
        Format a list item for keyboard navigation.
        
        Args:
            item: Item text
            index: Item index
            total: Total number of items
            
        Returns:
            Formatted list item
        """
        if not self._keyboard_nav_enabled:
            return f"  {index + 1}. {item}"
        
        # Add keyboard shortcut hint
        if index <= 9:
            key = str(index + 1)
        else:
            key = chr(ord('a') + index - 9)
        
        return f"  [{key}] {item}"
    
    def create_accessible_prompt(self, prompt_text: str, options: Optional[List[str]] = None) -> str:
        """
        Create an accessible prompt with keyboard hints.
        
        Args:
            prompt_text: The prompt text
            options: Optional list of options
            
        Returns:
            Formatted prompt string
        """
        if not self._keyboard_nav_enabled or not options:
            return prompt_text
        
        # Add keyboard hints for options
        lines = [prompt_text]
        lines.append("Options:")
        for i, option in enumerate(options, 1):
            if i <= 9:
                key = str(i)
            else:
                key = chr(ord('a') + i - 10)
            lines.append(f"  [{key}] {option}")
        
        return "\n".join(lines)