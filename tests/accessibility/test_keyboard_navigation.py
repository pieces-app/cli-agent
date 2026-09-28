"""
Tests for keyboard navigation features.
"""

import pytest
from pieces.accessibility.config import AccessibilityConfig
from pieces.accessibility.navigation import KeyboardNavigation, KeyboardShortcut


class TestKeyboardNavigation:
    """Test keyboard navigation functionality."""
    
    def test_keyboard_navigation_init(self):
        """Test keyboard navigation initialization."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True, reduced_motion=False)
        assert nav.keyboard_nav_enabled is True
        assert nav.reduced_motion is False
    
    def test_keyboard_navigation_disabled_by_default(self):
        """Test keyboard navigation is disabled by default."""
        nav = KeyboardNavigation()
        assert nav.keyboard_nav_enabled is False
    
    def test_reduced_motion_disabled_by_default(self):
        """Test reduced motion is disabled by default."""
        nav = KeyboardNavigation()
        assert nav.reduced_motion is False
    
    def test_register_shortcut(self):
        """Test registering keyboard shortcuts."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True)
        
        shortcut = KeyboardShortcut(
            key="a",
            description="Test action",
            action=lambda: "test",
            category="test"
        )
        
        nav.register_shortcut(shortcut)
        retrieved = nav.get_shortcut("a")
        
        assert retrieved is not None
        assert retrieved.key == "a"
        assert retrieved.description == "Test action"
    
    def test_get_shortcut_not_found(self):
        """Test getting non-existent shortcut."""
        nav = KeyboardNavigation()
        result = nav.get_shortcut("nonexistent")
        assert result is None
    
    def test_get_shortcuts_by_category(self):
        """Test getting shortcuts by category."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True)
        
        # Add custom shortcuts
        nav.register_shortcut(KeyboardShortcut(
            key="x", description="Action 1", action=lambda: None, category="test"
        ))
        nav.register_shortcut(KeyboardShortcut(
            key="y", description="Action 2", action=lambda: None, category="test"
        ))
        nav.register_shortcut(KeyboardShortcut(
            key="z", description="Action 3", action=lambda: None, category="other"
        ))
        
        test_shortcuts = nav.get_shortcuts_by_category("test")
        assert len(test_shortcuts) == 2
        assert all(s.category == "test" for s in test_shortcuts)
    
    def test_get_all_shortcuts(self):
        """Test getting all shortcuts."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True)
        
        all_shortcuts = nav.get_all_shortcuts()
        assert len(all_shortcuts) > 0  # Should have default shortcuts
    
    def test_format_shortcut_help_enabled(self):
        """Test shortcut help formatting when enabled."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True)
        help_text = nav.format_shortcut_help()
        
        assert "Keyboard Shortcuts" in help_text
        assert "q" in help_text
        assert "?" in help_text
    
    def test_format_shortcut_help_disabled(self):
        """Test shortcut help formatting when disabled."""
        nav = KeyboardNavigation(keyboard_nav_enabled=False)
        help_text = nav.format_shortcut_help()
        
        assert help_text == ""
    
    def test_should_animate_with_reduced_motion(self):
        """Test animation preference with reduced motion."""
        nav = KeyboardNavigation(reduced_motion=True)
        assert nav.should_animate() is False
    
    def test_should_animate_without_reduced_motion(self):
        """Test animation preference without reduced motion."""
        nav = KeyboardNavigation(reduced_motion=False)
        assert nav.should_animate() is True
    
    def test_get_animation_delay_with_reduced_motion(self):
        """Test animation delay with reduced motion."""
        nav = KeyboardNavigation(reduced_motion=True)
        delay = nav.get_animation_delay(0.5)
        assert delay == 0.0
    
    def test_get_animation_delay_without_reduced_motion(self):
        """Test animation delay without reduced motion."""
        nav = KeyboardNavigation(reduced_motion=False)
        delay = nav.get_animation_delay(0.5)
        assert delay == 0.5
    
    def test_create_menu_enabled(self):
        """Test menu creation with keyboard navigation enabled."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True)
        menu = nav.create_menu(["Option 1", "Option 2", "Option 3"], "Test Menu")
        
        assert "Test Menu" in menu
        assert "[1]" in menu
        assert "[2]" in menu
        assert "[3]" in menu
        assert "[q]" in menu
    
    def test_create_menu_disabled(self):
        """Test menu creation with keyboard navigation disabled."""
        nav = KeyboardNavigation(keyboard_nav_enabled=False)
        menu = nav.create_menu(["Option 1", "Option 2"], "Test Menu")
        
        assert "Test Menu" in menu
        assert "1. Option 1" in menu
        assert "2. Option 2" in menu
        assert "[1]" not in menu  # No keyboard hints
        assert "[q]" not in menu
    
    def test_create_progress_bar_with_reduced_motion(self):
        """Test progress bar with reduced motion."""
        nav = KeyboardNavigation(reduced_motion=True)
        progress = nav.create_progress_bar(5, 10)
        
        assert "5/10" in progress
        assert "50%" in progress
        assert "█" not in progress  # No visual bar
    
    def test_create_progress_bar_without_reduced_motion(self):
        """Test progress bar without reduced motion."""
        nav = KeyboardNavigation(reduced_motion=False)
        progress = nav.create_progress_bar(5, 10, width=20)
        
        assert "5/10" in progress
        assert "50%" in progress
        assert "█" in progress  # Has visual bar
    
    def test_format_list_item_enabled(self):
        """Test list item formatting with keyboard navigation."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True)
        item = nav.format_list_item("Test Item", 0, 5)
        
        assert "[1]" in item
        assert "Test Item" in item
    
    def test_format_list_item_disabled(self):
        """Test list item formatting without keyboard navigation."""
        nav = KeyboardNavigation(keyboard_nav_enabled=False)
        item = nav.format_list_item("Test Item", 0, 5)
        
        assert "1. Test Item" in item
        assert "[1]" not in item
    
    def test_format_list_item_beyond_9(self):
        """Test list item formatting beyond 9 items."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True)
        item = nav.format_list_item("Test Item", 10, 15)
        
        assert "[b]" in item  # Should use letter for items beyond 9
    
    def test_create_accessible_prompt_with_options(self):
        """Test accessible prompt with options."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True)
        prompt = nav.create_accessible_prompt("Choose an option:", ["A", "B", "C"])
        
        assert "Choose an option:" in prompt
        assert "Options:" in prompt
        assert "[1]" in prompt
        assert "[2]" in prompt
        assert "[3]" in prompt
    
    def test_create_accessible_prompt_without_options(self):
        """Test accessible prompt without options."""
        nav = KeyboardNavigation(keyboard_nav_enabled=True)
        prompt = nav.create_accessible_prompt("Enter value:")
        
        assert "Enter value:" in prompt
        assert "Options:" not in prompt
    
    def test_create_accessible_prompt_disabled(self):
        """Test accessible prompt with keyboard navigation disabled."""
        nav = KeyboardNavigation(keyboard_nav_enabled=False)
        prompt = nav.create_accessible_prompt("Choose:", ["A", "B"])
        
        assert "Choose:" in prompt
        assert "Options:" not in prompt  # No options list when disabled


class TestAccessibilityConfigKeyboardNav:
    """Test keyboard navigation detection in accessibility config."""
    
    def test_keyboard_navigation_env_variable(self):
        """Test keyboard navigation detection via environment variable."""
        import os
        original_kb_nav = os.environ.get('PIECES_KEYBOARD_NAVIGATION')
        
        try:
            os.environ['PIECES_KEYBOARD_NAVIGATION'] = '1'
            config = AccessibilityConfig()
            assert config.keyboard_navigation is True
            
            os.environ['PIECES_KEYBOARD_NAVIGATION'] = '0'
            config = AccessibilityConfig()
            assert config.keyboard_navigation is False
        finally:
            if original_kb_nav is not None:
                os.environ['PIECES_KEYBOARD_NAVIGATION'] = original_kb_nav
            elif 'PIECES_KEYBOARD_NAVIGATION' in os.environ:
                del os.environ['PIECES_KEYBOARD_NAVIGATION']
    
    def test_keyboard_navigation_auto_enabled_with_screen_reader(self):
        """Test keyboard navigation auto-enabled with screen reader."""
        import os
        original_screen_reader = os.environ.get('PIECES_SCREEN_READER')
        original_kb_nav = os.environ.get('PIECES_KEYBOARD_NAVIGATION')
        
        try:
            if 'PIECES_KEYBOARD_NAVIGATION' in os.environ:
                del os.environ['PIECES_KEYBOARD_NAVIGATION']
            
            os.environ['PIECES_SCREEN_READER'] = '1'
            config = AccessibilityConfig()
            assert config.keyboard_navigation is True  # Auto-enabled
        finally:
            if original_screen_reader is not None:
                os.environ['PIECES_SCREEN_READER'] = original_screen_reader
            elif 'PIECES_SCREEN_READER' in os.environ:
                del os.environ['PIECES_SCREEN_READER']
            if original_kb_nav is not None:
                os.environ['PIECES_KEYBOARD_NAVIGATION'] = original_kb_nav
            elif 'PIECES_KEYBOARD_NAVIGATION' in os.environ:
                del os.environ['PIECES_KEYBOARD_NAVIGATION']
    
    def test_reduced_motion_env_variable(self):
        """Test reduced motion detection via environment variable."""
        import os
        original_reduced_motion = os.environ.get('PIECES_REDUCED_MOTION')
        
        try:
            os.environ['PIECES_REDUCED_MOTION'] = '1'
            config = AccessibilityConfig()
            assert config.reduced_motion is True
            
            os.environ['PIECES_REDUCED_MOTION'] = '0'
            config = AccessibilityConfig()
            assert config.reduced_motion is False
        finally:
            if original_reduced_motion is not None:
                os.environ['PIECES_REDUCED_MOTION'] = original_reduced_motion
            elif 'PIECES_REDUCED_MOTION' in os.environ:
                del os.environ['PIECES_REDUCED_MOTION']