"""
Accessibility module for Pieces CLI.

This module provides accessibility features including:
- NO_COLOR support (https://no-color.org/)
- Color scheme detection
- Screen reader friendly output
- High contrast mode support
- Verbose/descriptive output modes
- Keyboard navigation helpers
- Cognitive accessibility features
"""

from pieces.accessibility.config import AccessibilityConfig
from pieces.accessibility.console import AccessibleConsole
from pieces.accessibility.navigation import KeyboardNavigation, KeyboardShortcut
from pieces.accessibility.cognitive import CognitiveAccessibility

__all__ = ['AccessibilityConfig', 'AccessibleConsole', 'KeyboardNavigation', 'KeyboardShortcut', 'CognitiveAccessibility']
