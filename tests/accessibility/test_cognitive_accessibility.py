"""
Tests for cognitive accessibility features.
"""

import pytest
from pieces.accessibility.config import AccessibilityConfig
from pieces.accessibility.cognitive import CognitiveAccessibility


class TestCognitiveAccessibility:
    """Test cognitive accessibility functionality."""
    
    def test_cognitive_accessibility_init(self):
        """Test cognitive accessibility initialization."""
        cognitive = CognitiveAccessibility(simplified_output=True, clear_language=True)
        assert cognitive.simplified_output is True
        assert cognitive.clear_language is True
    
    def test_cognitive_accessibility_disabled_by_default(self):
        """Test cognitive accessibility features are disabled by default."""
        cognitive = CognitiveAccessibility()
        assert cognitive.simplified_output is False
        assert cognitive.clear_language is False
    
    def test_simplify_error_connection_refused(self):
        """Test simplifying connection refused error."""
        cognitive = CognitiveAccessibility(clear_language=True)
        error = "Error: Connection refused"
        simplified = cognitive.simplify_error(error)
        
        assert "Cannot connect" in simplified
        assert "PiecesOS" in simplified
        assert "refused" not in simplified.lower()
    
    def test_simplify_error_connection_timeout(self):
        """Test simplifying connection timeout error."""
        cognitive = CognitiveAccessibility(clear_language=True)
        error = "Error: Connection timeout"
        simplified = cognitive.simplify_error(error)
        
        assert "too long" in simplified
        assert "internet connection" in simplified
        assert "timeout" not in simplified.lower()
    
    def test_simplify_error_authentication_failed(self):
        """Test simplifying authentication failed error."""
        cognitive = CognitiveAccessibility(clear_language=True)
        error = "Error: Authentication failed"
        simplified = cognitive.simplify_error(error)
        
        assert "verify your identity" in simplified
        assert "login credentials" in simplified
        assert "authentication" not in simplified.lower()
    
    def test_simplify_error_unknown(self):
        """Test simplifying unknown error."""
        cognitive = CognitiveAccessibility(clear_language=True)
        error = "Error: Something went terribly wrong"
        simplified = cognitive.simplify_error(error)
        
        assert "An error occurred" in simplified
        assert "Something went terribly wrong" in simplified
    
    def test_simplify_text_jargon(self):
        """Test simplifying technical jargon."""
        cognitive = CognitiveAccessibility(clear_language=True)
        text = "Execute the program with proper configuration"
        simplified = cognitive._simplify_text(text)
        
        assert "run" in simplified
        assert "settings" in simplified
        assert "execute" not in simplified.lower()
        assert "configuration" not in simplified.lower()
    
    def test_simplify_text_multiple_jargon(self):
        """Test simplifying multiple technical terms."""
        cognitive = CognitiveAccessibility(clear_language=True)
        text = "Initialize the daemon with proper parameters"
        simplified = cognitive._simplify_text(text)
        
        assert "start" in simplified
        assert "background program" in simplified
        assert "options" in simplified
        assert "initialize" not in simplified.lower()
        assert "daemon" not in simplified.lower()
        assert "parameters" not in simplified.lower()
    
    def test_get_simple_command_description(self):
        """Test getting simple command descriptions."""
        cognitive = CognitiveAccessibility(clear_language=True)
        
        desc = cognitive.get_simple_command_description("list")
        assert "Show all your saved code snippets" in desc
        
        desc = cognitive.get_simple_command_description("create")
        assert "Save a new code snippet" in desc
    
    def test_get_simple_command_description_unknown(self):
        """Test getting description for unknown command."""
        cognitive = CognitiveAccessibility(clear_language=True)
        desc = cognitive.get_simple_command_description("unknown_command")
        assert desc == ""
    
    def test_get_simple_command_description_disabled(self):
        """Test command descriptions when clear language is disabled."""
        cognitive = CognitiveAccessibility(clear_language=False)
        desc = cognitive.get_simple_command_description("list")
        assert desc == ""
    
    def test_format_help_simple(self):
        """Test formatting help in simple language."""
        cognitive = CognitiveAccessibility(clear_language=True)
        original_help = "List all materials in your Pieces Drive"
        formatted = cognitive.format_help_simple("list", original_help)
        
        assert "What this does" in formatted
        assert "Show all your saved code snippets" in formatted
        assert "More details" in formatted
    
    def test_format_help_simple_unknown_command(self):
        """Test formatting help for unknown command."""
        cognitive = CognitiveAccessibility(clear_language=True)
        original_help = "Some help text"
        formatted = cognitive.format_help_simple("unknown", original_help)
        
        assert formatted == original_help  # No simple description available
    
    def test_simplify_list_output_small(self):
        """Test simplifying small list (no truncation needed)."""
        cognitive = CognitiveAccessibility(simplified_output=True)
        items = ["Item 1", "Item 2", "Item 3"]
        simplified = cognitive.simplify_list_output(items, max_items=10)
        
        assert "Item 1" in simplified
        assert "Item 2" in simplified
        assert "Item 3" in simplified
        assert "more items" not in simplified
    
    def test_simplify_list_output_large(self):
        """Test simplifying large list (truncation needed)."""
        cognitive = CognitiveAccessibility(simplified_output=True)
        items = [f"Item {i}" for i in range(20)]
        simplified = cognitive.simplify_list_output(items, max_items=10)
        
        assert "more items" in simplified
        assert "Item 0" in simplified
        assert "Item 19" in simplified
        assert "Item 10" not in simplified  # Middle items should be truncated
    
    def test_simplify_list_output_disabled(self):
        """Test list output when simplified output is disabled."""
        cognitive = CognitiveAccessibility(simplified_output=False)
        items = ["Item 1", "Item 2", "Item 3"]
        simplified = cognitive.simplify_list_output(items, max_items=10)
        
        assert simplified == "Item 1\nItem 2\nItem 3"
    
    def test_format_progress_simple(self):
        """Test formatting progress in simple terms."""
        cognitive = CognitiveAccessibility(simplified_output=True)
        progress = cognitive.format_progress_simple("Downloading", 5, 10)
        
        assert "halfway" in progress.lower()
        assert "5 of 10" in progress
    
    def test_format_progress_simple_started(self):
        """Test formatting progress when just started."""
        cognitive = CognitiveAccessibility(simplified_output=True)
        progress = cognitive.format_progress_simple("Downloading", 2, 10)
        
        assert "started" in progress.lower()
    
    def test_format_progress_simple_nearly_done(self):
        """Test formatting progress when nearly done."""
        cognitive = CognitiveAccessibility(simplified_output=True)
        progress = cognitive.format_progress_simple("Downloading", 9, 10)
        
        assert "complete" in progress.lower()
    
    def test_format_progress_simple_disabled(self):
        """Test progress formatting when simplified output is disabled."""
        cognitive = CognitiveAccessibility(simplified_output=False)
        progress = cognitive.format_progress_simple("Downloading", 5, 10)
        
        assert progress == "Downloading: 5/10"
    
    def test_simplify_confirmation(self):
        """Test simplifying confirmation prompts."""
        cognitive = CognitiveAccessibility(clear_language=True)
        prompt = "Would you like to continue?"
        simplified = cognitive.simplify_confirmation(prompt)
        
        assert "Do you want to" in simplified
        assert "yes or no" in simplified
    
    def test_simplify_confirmation_already_simple(self):
        """Test simplifying already simple confirmation."""
        cognitive = CognitiveAccessibility(clear_language=True)
        prompt = "Are you sure?"
        simplified = cognitive.simplify_confirmation(prompt)
        
        assert "yes or no" in simplified
    
    def test_simplify_confirmation_disabled(self):
        """Test confirmation when clear language is disabled."""
        cognitive = CognitiveAccessibility(clear_language=False)
        prompt = "Would you like to continue?"
        simplified = cognitive.simplify_confirmation(prompt)
        
        assert simplified == prompt
    
    def test_get_context_help_error(self):
        """Test getting context help for error."""
        cognitive = CognitiveAccessibility(clear_language=True)
        help_text = cognitive.get_context_help("error occurred")
        
        assert "Something went wrong" in help_text
        assert "help" in help_text.lower()
    
    def test_get_context_help_permission(self):
        """Test getting context help for permission error."""
        cognitive = CognitiveAccessibility(clear_language=True)
        help_text = cognitive.get_context_help("permission denied")
        
        assert "permission" in help_text.lower()
        assert "logged in" in help_text
    
    def test_get_context_help_network(self):
        """Test getting context help for network error."""
        cognitive = CognitiveAccessibility(clear_language=True)
        help_text = cognitive.get_context_help("network error")
        
        assert "internet connection" in help_text
    
    def test_get_context_help_general(self):
        """Test getting general context help."""
        cognitive = CognitiveAccessibility(clear_language=True)
        help_text = cognitive.get_context_help("something else")
        
        assert "help" in help_text.lower()
        assert "Ctrl+C" in help_text
    
    def test_get_context_help_disabled(self):
        """Test context help when clear language is disabled."""
        cognitive = CognitiveAccessibility(clear_language=False)
        help_text = cognitive.get_context_help("error")
        
        assert help_text == ""
    
    def test_format_output_simple_with_clear_language(self):
        """Test formatting output with clear language."""
        cognitive = CognitiveAccessibility(clear_language=True)
        text = "Execute the configuration"
        formatted = cognitive.format_output_simple(text)
        
        assert "run" in formatted
        assert "settings" in formatted
    
    def test_format_output_simple_with_simplified_output(self):
        """Test formatting output with simplified output (removes debug info)."""
        cognitive = CognitiveAccessibility(simplified_output=True)
        text = "Traceback (most recent call last):\nFile test.py line 1\nError occurred"
        formatted = cognitive.format_output_simple(text)
        
        assert "Traceback" not in formatted
        assert "Error occurred" in formatted
    
    def test_format_output_simple_disabled(self):
        """Test output formatting when both features are disabled."""
        cognitive = CognitiveAccessibility(simplified_output=False, clear_language=False)
        text = "Execute the configuration"
        formatted = cognitive.format_output_simple(text)
        
        assert formatted == text


class TestAccessibilityConfigCognitive:
    """Test cognitive accessibility detection in accessibility config."""
    
    def test_simplified_output_env_variable(self):
        """Test simplified output detection via environment variable."""
        import os
        original_simplified = os.environ.get('PIECES_SIMPLIFIED_OUTPUT')
        
        try:
            os.environ['PIECES_SIMPLIFIED_OUTPUT'] = '1'
            config = AccessibilityConfig()
            assert config.simplified_output is True
            
            os.environ['PIECES_SIMPLIFIED_OUTPUT'] = '0'
            config = AccessibilityConfig()
            assert config.simplified_output is False
        finally:
            if original_simplified is not None:
                os.environ['PIECES_SIMPLIFIED_OUTPUT'] = original_simplified
            elif 'PIECES_SIMPLIFIED_OUTPUT' in os.environ:
                del os.environ['PIECES_SIMPLIFIED_OUTPUT']
    
    def test_simplified_output_auto_enabled_with_screen_reader(self):
        """Test simplified output auto-enabled with screen reader."""
        import os
        original_screen_reader = os.environ.get('PIECES_SCREEN_READER')
        original_simplified = os.environ.get('PIECES_SIMPLIFIED_OUTPUT')
        
        try:
            if 'PIECES_SIMPLIFIED_OUTPUT' in os.environ:
                del os.environ['PIECES_SIMPLIFIED_OUTPUT']
            
            os.environ['PIECES_SCREEN_READER'] = '1'
            config = AccessibilityConfig()
            assert config.simplified_output is True  # Auto-enabled
        finally:
            if original_screen_reader is not None:
                os.environ['PIECES_SCREEN_READER'] = original_screen_reader
            elif 'PIECES_SCREEN_READER' in os.environ:
                del os.environ['PIECES_SCREEN_READER']
            if original_simplified is not None:
                os.environ['PIECES_SIMPLIFIED_OUTPUT'] = original_simplified
            elif 'PIECES_SIMPLIFIED_OUTPUT' in os.environ:
                del os.environ['PIECES_SIMPLIFIED_OUTPUT']
    
    def test_clear_language_env_variable(self):
        """Test clear language detection via environment variable."""
        import os
        original_clear_lang = os.environ.get('PIECES_CLEAR_LANGUAGE')
        
        try:
            os.environ['PIECES_CLEAR_LANGUAGE'] = '1'
            config = AccessibilityConfig()
            assert config.clear_language is True
            
            os.environ['PIECES_CLEAR_LANGUAGE'] = '0'
            config = AccessibilityConfig()
            assert config.clear_language is False
        finally:
            if original_clear_lang is not None:
                os.environ['PIECES_CLEAR_LANGUAGE'] = original_clear_lang
            elif 'PIECES_CLEAR_LANGUAGE' in os.environ:
                del os.environ['PIECES_CLEAR_LANGUAGE']
    
    def test_clear_language_auto_enabled_with_simplified_output(self):
        """Test clear language auto-enabled with simplified output."""
        import os
        original_simplified = os.environ.get('PIECES_SIMPLIFIED_OUTPUT')
        original_clear_lang = os.environ.get('PIECES_CLEAR_LANGUAGE')
        
        try:
            if 'PIECES_CLEAR_LANGUAGE' in os.environ:
                del os.environ['PIECES_CLEAR_LANGUAGE']
            
            os.environ['PIECES_SIMPLIFIED_OUTPUT'] = '1'
            config = AccessibilityConfig()
            assert config.clear_language is True  # Auto-enabled
        finally:
            if original_simplified is not None:
                os.environ['PIECES_SIMPLIFIED_OUTPUT'] = original_simplified
            elif 'PIECES_SIMPLIFIED_OUTPUT' in os.environ:
                del os.environ['PIECES_SIMPLIFIED_OUTPUT']
            if original_clear_lang is not None:
                os.environ['PIECES_CLEAR_LANGUAGE'] = original_clear_lang
            elif 'PIECES_CLEAR_LANGUAGE' in os.environ:
                del os.environ['PIECES_CLEAR_LANGUAGE']