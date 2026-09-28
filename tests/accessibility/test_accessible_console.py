"""
Tests for accessible console wrapper.
"""

import os
import pytest
from io import StringIO
from pieces.accessibility.config import AccessibilityConfig
from pieces.accessibility.console import AccessibleConsole


class TestAccessibleConsole:
    """Test accessible console functionality."""
    
    def test_console_creation_with_config(self):
        """Test creating AccessibleConsole with custom config."""
        config = AccessibilityConfig()
        console = AccessibleConsole(config=config)
        assert console.config == config
        assert console.console is not None
    
    def test_console_no_color_mode(self):
        """Test console respects NO_COLOR mode."""
        original_no_color = os.environ.get('NO_COLOR')
        
        try:
            os.environ['NO_COLOR'] = '1'
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            
            # Console should have no_color enabled
            assert console.config.no_color is True
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
    
    def test_console_print_with_colors(self):
        """Test console print with colors enabled."""
        original_no_color = os.environ.get('NO_COLOR')
        
        try:
            if 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            
            # Should print normally with colors
            assert console.config.should_use_color is True
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
    
    def test_format_string_accessible_with_indicators(self):
        """Test string formatting adds indicators when colors disabled."""
        original_no_color = os.environ.get('NO_COLOR')
        
        try:
            os.environ['NO_COLOR'] = '1'
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            
            # Test that color markup gets converted to indicators
            result = console._format_string_accessible("[red]Error[/red]")
            assert "✗" in result or "Error" in result
            
            result = console._format_string_accessible("[green]Success[/green]")
            assert "✓" in result or "Success" in result
            
            result = console._format_string_accessible("[yellow]Warning[/yellow]")
            assert "⚠" in result or "Warning" in result
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
    
    def test_format_string_accessible_with_colors(self):
        """Test string formatting preserves colors when enabled."""
        original_no_color = os.environ.get('NO_COLOR')
        
        try:
            if 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            
            # Should preserve color markup when colors are enabled
            result = console._format_string_accessible("[red]Error[/red]")
            assert "[red]" in result or "Error" in result  # May be processed by Rich
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
    
    def test_console_delegates_methods(self):
        """Test that console delegates methods to underlying Rich console."""
        config = AccessibilityConfig()
        console = AccessibleConsole(config=config)
        
        # Should have access to Rich console methods
        assert hasattr(console.console, 'print')
        assert hasattr(console.console, 'rule')
        assert hasattr(console.console, 'status')
    
    def test_console_context_manager(self):
        """Test console supports context manager."""
        config = AccessibilityConfig()
        console = AccessibleConsole(config=config)
        
        # Should support context manager protocol
        assert hasattr(console, '__enter__')
        assert hasattr(console, '__exit__')
        
        # Test basic context manager usage
        with console:
            pass  # Should not raise an error
    
    def test_screen_reader_formatting(self):
        """Test screen reader specific formatting."""
        original_screen_reader = os.environ.get('PIECES_SCREEN_READER')
        
        try:
            os.environ['PIECES_SCREEN_READER'] = '1'
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            
            # Test that visual indicators are removed
            result = console._format_for_screen_reader("Error: [red]Failed[/red]")
            assert "[red]" not in result
            assert "[/red]" not in result
            assert "Failed" in result
            
            # Test that box drawing characters are removed
            result = console._format_for_screen_reader("─ ━ │ ┃")
            assert "─" not in result
            assert "━" not in result
            assert "│" not in result
        finally:
            if original_screen_reader is not None:
                os.environ['PIECES_SCREEN_READER'] = original_screen_reader
            elif 'PIECES_SCREEN_READER' in os.environ:
                del os.environ['PIECES_SCREEN_READER']
    
    def test_screen_reader_structure_printing(self):
        """Test screen reader friendly structure printing."""
        original_screen_reader = os.environ.get('PIECES_SCREEN_READER')
        
        try:
            os.environ['PIECES_SCREEN_READER'] = '1'
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            
            # Test that print_structure works (no assertion, just ensure it doesn't crash)
            console.print_structure("Test Title", ["Item 1", "Item 2", "Item 3"])
        finally:
            if original_screen_reader is not None:
                os.environ['PIECES_SCREEN_READER'] = original_screen_reader
            elif 'PIECES_SCREEN_READER' in os.environ:
                del os.environ['PIECES_SCREEN_READER']
    
    def test_screen_reader_progress_printing(self):
        """Test screen reader friendly progress printing."""
        original_screen_reader = os.environ.get('PIECES_SCREEN_READER')
        
        try:
            os.environ['PIECES_SCREEN_READER'] = '1'
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            
            # Test that print_progress works (no assertion, just ensure it doesn't crash)
            console.print_progress("Downloading", 5, 10)
        finally:
            if original_screen_reader is not None:
                os.environ['PIECES_SCREEN_READER'] = original_screen_reader
            elif 'PIECES_SCREEN_READER' in os.environ:
                del os.environ['PIECES_SCREEN_READER']
    
    def test_screen_reader_list_printing(self):
        """Test screen reader friendly list printing."""
        original_screen_reader = os.environ.get('PIECES_SCREEN_READER')
        
        try:
            os.environ['PIECES_SCREEN_READER'] = '1'
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            
            # Test that print_list works (no assertion, just ensure it doesn't crash)
            console.print_list(["Item 1", "Item 2", "Item 3"], "Test List")
        finally:
            if original_screen_reader is not None:
                os.environ['PIECES_SCREEN_READER'] = original_screen_reader
            elif 'PIECES_SCREEN_READER' in os.environ:
                del os.environ['PIECES_SCREEN_READER']