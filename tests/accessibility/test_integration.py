"""
Integration tests for accessibility features.

Tests that verify all accessibility features work together correctly.
"""

import os
import pytest
from pieces.accessibility.config import AccessibilityConfig
from pieces.accessibility.console import AccessibleConsole
from pieces.accessibility.navigation import KeyboardNavigation
from pieces.accessibility.cognitive import CognitiveAccessibility


class TestAccessibilityIntegration:
    """Test integration of all accessibility features."""
    
    def test_all_features_with_screen_reader(self):
        """Test that enabling screen reader enables related features."""
        original_screen_reader = os.environ.get('PIECES_SCREEN_READER')
        
        try:
            os.environ['PIECES_SCREEN_READER'] = '1'
            config = AccessibilityConfig()
            
            # Screen reader should enable related features
            assert config.screen_reader is True
            assert config.verbose is True  # Auto-enabled
            assert config.keyboard_navigation is True  # Auto-enabled
            assert config.simplified_output is True  # Auto-enabled
            assert config.clear_language is True  # Auto-enabled
        finally:
            if original_screen_reader is not None:
                os.environ['PIECES_SCREEN_READER'] = original_screen_reader
            elif 'PIECES_SCREEN_READER' in os.environ:
                del os.environ['PIECES_SCREEN_READER']
    
    def test_no_color_with_screen_reader(self):
        """Test NO_COLOR interaction with screen reader mode."""
        original_screen_reader = os.environ.get('PIECES_SCREEN_READER')
        original_no_color = os.environ.get('NO_COLOR')
        
        try:
            os.environ['PIECES_SCREEN_READER'] = '1'
            os.environ['NO_COLOR'] = '1'
            config = AccessibilityConfig()
            
            # Both should be enabled
            assert config.screen_reader is True
            assert config.no_color is True
            
            # Screen reader should use descriptive indicators
            assert config.get_text_indicator('success') == '[SUCCESS]'
        finally:
            if original_screen_reader is not None:
                os.environ['PIECES_SCREEN_READER'] = original_screen_reader
            elif 'PIECES_SCREEN_READER' in os.environ:
                del os.environ['PIECES_SCREEN_READER']
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
    
    def test_console_with_all_features(self):
        """Test AccessibleConsole with multiple accessibility features enabled."""
        original_screen_reader = os.environ.get('PIECES_SCREEN_READER')
        original_no_color = os.environ.get('NO_COLOR')
        
        try:
            os.environ['PIECES_SCREEN_READER'] = '1'
            os.environ['NO_COLOR'] = '1'
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            
            # Console should respect all settings
            assert console.config.screen_reader is True
            assert console.config.no_color is True
            assert console.config.verbose is True
            
            # Test formatting with screen reader
            result = console._format_for_screen_reader("[red]Error[/red]")
            assert "[red]" not in result
            assert "Error" in result
        finally:
            if original_screen_reader is not None:
                os.environ['PIECES_SCREEN_READER'] = original_screen_reader
            elif 'PIECES_SCREEN_READER' in os.environ:
                del os.environ['PIECES_SCREEN_READER']
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
    
    def test_keyboard_navigation_with_reduced_motion(self):
        """Test keyboard navigation with reduced motion."""
        original_kb_nav = os.environ.get('PIECES_KEYBOARD_NAVIGATION')
        original_reduced_motion = os.environ.get('PIECES_REDUCED_MOTION')
        
        try:
            os.environ['PIECES_KEYBOARD_NAVIGATION'] = '1'
            os.environ['PIECES_REDUCED_MOTION'] = '1'
            config = AccessibilityConfig()
            nav = KeyboardNavigation(keyboard_nav_enabled=config.keyboard_navigation, 
                                   reduced_motion=config.reduced_motion)
            
            # Both should be enabled
            assert nav.keyboard_nav_enabled is True
            assert nav.reduced_motion is True
            
            # Progress bar should be simple (no visual bar)
            progress = nav.create_progress_bar(5, 10)
            assert "█" not in progress  # No visual bar with reduced motion
            assert "5/10" in progress
        finally:
            if original_kb_nav is not None:
                os.environ['PIECES_KEYBOARD_NAVIGATION'] = original_kb_nav
            elif 'PIECES_KEYBOARD_NAVIGATION' in os.environ:
                del os.environ['PIECES_KEYBOARD_NAVIGATION']
            if original_reduced_motion is not None:
                os.environ['PIECES_REDUCED_MOTION'] = original_reduced_motion
            elif 'PIECES_REDUCED_MOTION' in os.environ:
                del os.environ['PIECES_REDUCED_MOTION']
    
    def test_cognitive_with_verbose(self):
        """Test cognitive accessibility with verbose mode."""
        original_verbose = os.environ.get('PIECES_VERBOSE')
        original_clear_lang = os.environ.get('PIECES_CLEAR_LANGUAGE')
        
        try:
            os.environ['PIECES_VERBOSE'] = '1'
            os.environ['PIECES_CLEAR_LANGUAGE'] = '1'
            config = AccessibilityConfig()
            cognitive = CognitiveAccessibility(simplified_output=config.simplified_output,
                                            clear_language=config.clear_language)
            
            # Both should be enabled
            assert config.verbose is True
            assert config.clear_language is True
            assert cognitive.clear_language is True
            
            # Test error simplification
            error = cognitive.simplify_error("Connection refused")
            assert "Cannot connect" in error
            assert "refused" not in error.lower()
        finally:
            if original_verbose is not None:
                os.environ['PIECES_VERBOSE'] = original_verbose
            elif 'PIECES_VERBOSE' in os.environ:
                del os.environ['PIECES_VERBOSE']
            if original_clear_lang is not None:
                os.environ['PIECES_CLEAR_LANGUAGE'] = original_clear_lang
            elif 'PIECES_CLEAR_LANGUAGE' in os.environ:
                del os.environ['PIECES_CLEAR_LANGUAGE']
    
    def test_priority_order(self):
        """Test that environment variable priority is correct."""
        original_no_color = os.environ.get('NO_COLOR')
        original_color_scheme = os.environ.get('PIECES_COLOR_SCHEME')
        
        try:
            # NO_COLOR should have highest priority
            os.environ['NO_COLOR'] = '1'
            os.environ['PIECES_COLOR_SCHEME'] = 'high_contrast'
            config = AccessibilityConfig()
            
            assert config.no_color is True
            assert config.color_scheme.value == 'monochrome'  # NO_COLOR forces monochrome
        finally:
            if original_no_color is not None:
                os.environ['NO_COLOR'] = original_no_color
            elif 'NO_COLOR' in os.environ:
                del os.environ['NO_COLOR']
            if original_color_scheme is not None:
                os.environ['PIECES_COLOR_SCHEME'] = original_color_scheme
            elif 'PIECES_COLOR_SCHEME' in os.environ:
                del os.environ['PIECES_COLOR_SCHEME']
    
    def test_default_state(self):
        """Test that default state has no accessibility features enabled."""
        # Clear all environment variables
        env_vars_to_clear = [
            'NO_COLOR', 'PIECES_COLOR_SCHEME', 'PIECES_SCREEN_READER',
            'PIECES_VERBOSE', 'PIECES_KEYBOARD_NAVIGATION', 'PIECES_REDUCED_MOTION',
            'PIECES_SIMPLIFIED_OUTPUT', 'PIECES_CLEAR_LANGUAGE'
        ]
        
        original_values = {}
        for var in env_vars_to_clear:
            original_values[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            config = AccessibilityConfig()
            
            # Nothing should be enabled by default
            assert config.no_color is False
            assert config.screen_reader is False
            assert config.verbose is False
            assert config.keyboard_navigation is False
            assert config.reduced_motion is False
            assert config.simplified_output is False
            assert config.clear_language is False
        finally:
            # Restore original values
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
                elif var in os.environ:
                    del os.environ[var]
    
    def test_full_accessibility_stack(self):
        """Test the full accessibility stack with all features enabled."""
        env_vars = {
            'NO_COLOR': '1',
            'PIECES_SCREEN_READER': '1',
            'PIECES_VERBOSE': '1',
            'PIECES_KEYBOARD_NAVIGATION': '1',
            'PIECES_REDUCED_MOTION': '1',
            'PIECES_SIMPLIFIED_OUTPUT': '1',
            'PIECES_CLEAR_LANGUAGE': '1'
        }
        
        original_values = {}
        for var, value in env_vars.items():
            original_values[var] = os.environ.get(var)
            os.environ[var] = value
        
        try:
            config = AccessibilityConfig()
            console = AccessibleConsole(config=config)
            nav = KeyboardNavigation(keyboard_nav_enabled=config.keyboard_navigation,
                                   reduced_motion=config.reduced_motion)
            cognitive = CognitiveAccessibility(simplified_output=config.simplified_output,
                                            clear_language=config.clear_language)
            
            # All features should be enabled
            assert config.no_color is True
            assert config.screen_reader is True
            assert config.verbose is True
            assert config.keyboard_navigation is True
            assert config.reduced_motion is True
            assert config.simplified_output is True
            assert config.clear_language is True
            
            # Test console formatting
            assert console.config.screen_reader is True
            assert console.config.no_color is True
            
            # Test keyboard navigation
            assert nav.keyboard_nav_enabled is True
            assert nav.reduced_motion is True
            assert nav.should_animate() is False
            
            # Test cognitive accessibility
            assert cognitive.simplified_output is True
            assert cognitive.clear_language is True
            
            # Test error simplification
            error = cognitive.simplify_error("Connection refused")
            assert "Cannot connect" in error
            
            # Test progress bar (should be simple)
            progress = nav.create_progress_bar(5, 10)
            assert "█" not in progress
            
        finally:
            # Restore original values
            for var, value in original_values.items():
                if value is not None:
                    os.environ[var] = value
                elif var in os.environ:
                    del os.environ[var]