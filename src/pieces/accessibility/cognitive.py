"""
Cognitive accessibility helpers for Pieces CLI.

Provides utilities for cognitive accessibility including:
- Simplified output formatting
- Clear language processing
- Error message simplification
- Context-aware help
"""

from typing import Optional, Dict, List
import re


class CognitiveAccessibility:
    """
    Manages cognitive accessibility features.
    
    Provides simplified output and clear language features for users
    who benefit from reduced complexity and clearer communication.
    """
    
    def __init__(self, simplified_output: bool = False, clear_language: bool = False):
        """
        Initialize cognitive accessibility manager.
        
        Args:
            simplified_output: Whether simplified output mode is enabled
            clear_language: Whether clear language mode is enabled
        """
        self._simplified_output = simplified_output
        self._clear_language = clear_language
        self._error_translations = self._build_error_translations()
        self._command_descriptions = self._build_command_descriptions()
    
    @property
    def simplified_output(self) -> bool:
        """Check if simplified output is enabled."""
        return self._simplified_output
    
    @property
    def clear_language(self) -> bool:
        """Check if clear language is enabled."""
        return self._clear_language
    
    def _build_error_translations(self) -> Dict[str, str]:
        """Build dictionary of technical error to simple language translations."""
        return {
            # Common technical errors to simple language
            "connection refused": "Cannot connect to the service. Please check if PiecesOS is running.",
            "connection timeout": "Connection took too long. Please check your internet connection.",
            "authentication failed": "Could not verify your identity. Please check your login credentials.",
            "permission denied": "You don't have permission to do this. Please check your access rights.",
            "file not found": "The file could not be found. Please check the file path.",
            "invalid input": "The information you provided is not correct. Please check and try again.",
            "network unreachable": "Cannot reach the network. Please check your internet connection.",
            "operation not permitted": "This action is not allowed. Please contact support if you need help.",
            "resource temporarily unavailable": "The service is busy. Please wait a moment and try again.",
            "segmentation fault": "The program encountered an unexpected error. Please restart and try again.",
            "out of memory": "The program ran out of memory. Please close other programs and try again.",
            "disk full": "There is no space left on your disk. Please free up space and try again.",
            "unknown error": "Something went wrong. Please try again or contact support for help.",
        }
    
    def _build_command_descriptions(self) -> Dict[str, str]:
        """Build dictionary of simple command descriptions."""
        return {
            "list": "Show all your saved code snippets",
            "create": "Save a new code snippet from your clipboard",
            "edit": "Change the name or type of a snippet",
            "delete": "Remove a snippet",
            "search": "Find snippets by searching for words",
            "ask": "Ask an AI question about your code",
            "help": "Show information about how to use this program",
            "config": "Change program settings",
            "login": "Sign in to your account",
            "logout": "Sign out of your account",
        }
    
    def simplify_error(self, error_message: str) -> str:
        """
        Simplify technical error messages into clear language.
        
        Args:
            error_message: Original technical error message
            
        Returns:
            Simplified error message in clear language
        """
        if not self._clear_language:
            return error_message
        
        # Convert to lowercase for matching
        error_lower = error_message.lower()
        
        # Check for known error patterns
        for technical, simple in self._error_translations.items():
            if technical in error_lower:
                return simple
        
        # If no match, provide a generic clear message
        return f"An error occurred: {self._simplify_text(error_message)}"
    
    def _simplify_text(self, text: str) -> str:
        """
        Simplify text by removing technical jargon and complex terms.
        
        Args:
            text: Original text
            
        Returns:
            Simplified text
        """
        # Remove common technical jargon
        jargon_replacements = {
            "execute": "run",
            "terminate": "stop",
            "initialize": "start",
            "configuration": "settings",
            "authentication": "login",
            "authorization": "permission",
            "enumeration": "list",
            "parameter": "option",
            "parameters": "options",
            "argument": "input",
            "directory": "folder",
            "executable": "program",
            "process": "program",
            "daemon": "background program",
            "syntax": "format",
            "parse": "read",
            "render": "show",
            "invoke": "use",
            "allocate": "reserve",
            "deallocate": "free",
            "buffer": "storage",
            "cache": "saved data",
            "protocol": "rules",
            "latency": "delay",
            "throughput": "speed",
        }
        
        words = text.split()
        simplified_words = []
        
        for word in words:
            # Remove punctuation for matching
            clean_word = word.strip('.,!?;:')
            if clean_word.lower() in jargon_replacements:
                # Keep original punctuation
                punctuation = word[len(clean_word):]
                simplified_words.append(jargon_replacements[clean_word.lower()] + punctuation)
            else:
                simplified_words.append(word)
        
        return ' '.join(simplified_words)
    
    def get_simple_command_description(self, command: str) -> str:
        """
        Get a simple description for a command.
        
        Args:
            command: Command name
            
        Returns:
            Simple description of the command
        """
        if not self._clear_language:
            return ""
        
        return self._command_descriptions.get(command.lower(), "")
    
    def format_help_simple(self, command: str, original_help: str) -> str:
        """
        Format help text in simple language.
        
        Args:
            command: Command name
            original_help: Original help text
            
        Returns:
            Simplified help text
        """
        if not self._clear_language:
            return original_help
        
        simple_desc = self.get_simple_command_description(command)
        if simple_desc:
            lines = [f"What this does: {simple_desc}"]
            lines.append(f"More details: {original_help}")
            return "\n".join(lines)
        
        return original_help
    
    def simplify_list_output(self, items: List[str], max_items: int = 10) -> str:
        """
        Simplify list output to reduce cognitive load.
        
        Args:
            items: List of items to display
            max_items: Maximum number of items to show at once
            
        Returns:
            Simplified list output
        """
        if not self._simplified_output:
            return "\n".join(items)
        
        total = len(items)
        
        if total <= max_items:
            return "\n".join(items)
        
        # Show first few and last few items
        first_part = items[:max_items // 2]
        last_part = items[-(max_items // 2):]
        
        lines = []
        lines.extend(first_part)
        lines.append(f"... ({total - max_items} more items not shown) ...")
        lines.extend(last_part)
        
        return "\n".join(lines)
    
    def format_progress_simple(self, message: str, current: int, total: int) -> str:
        """
        Format progress information in simple terms.
        
        Args:
            message: Progress message
            current: Current progress value
            total: Total progress value
            
        Returns:
            Simplified progress message
        """
        if not self._simplified_output:
            return f"{message}: {current}/{total}"
        
        if total == 0:
            return f"{message}: Getting started"
        
        percentage = (current / total) * 100
        
        # Use simple descriptions for progress
        if percentage < 25:
            status = "just started"
        elif percentage < 50:
            status = "about one-quarter done"
        elif percentage < 75:
            status = "about halfway done"
        elif percentage < 90:
            status = "almost finished"
        else:
            status = "nearly complete"
        
        return f"{message}: {status} ({current} of {total})"
    
    def simplify_confirmation(self, prompt: str) -> str:
        """
        Simplify confirmation prompts.
        
        Args:
            prompt: Original confirmation prompt
            
        Returns:
            Simplified confirmation prompt
        """
        if not self._clear_language:
            return prompt
        
        # Make the prompt more direct
        simplified = prompt.replace("Would you like to", "Do you want to")
        simplified = simplified.replace("Are you sure you want to", "Are you sure you want to")
        simplified = simplified.replace("Please confirm", "Please confirm")
        
        # Add clear yes/no guidance
        if "?" not in simplified:
            simplified += "?"
        
        simplified += " (yes or no)"
        
        return simplified
    
    def get_context_help(self, context: str) -> str:
        """
        Get context-aware help information.
        
        Args:
            context: Current context or command
            
        Returns:
            Contextual help in simple language
        """
        if not self._clear_language:
            return ""
        
        help_messages = {
            "network": "Check your internet connection and try again.",
            "connection": "Check your internet connection and try again.",
            "permission": "You don't have permission. Check if you're logged in correctly.",
            "file": "Make sure the file exists and you can access it.",
            "error": "Something went wrong. Try the action again or type 'help' for assistance.",
            "general": "Type 'help' to see available commands, or press Ctrl+C to cancel.",
        }
        
        # Determine context from error keywords
        context_lower = context.lower()
        for key, message in help_messages.items():
            if key in context_lower:
                return message
        
        return help_messages["general"]
    
    def format_output_simple(self, text: str) -> str:
        """
        Format general output in simple, clear language.
        
        Args:
            text: Original text
            
        Returns:
            Simplified text
        """
        if not self._simplified_output and not self._clear_language:
            return text
        
        # Apply simplifications
        simplified = text
        
        if self._clear_language:
            simplified = self._simplify_text(simplified)
        
        # Remove excessive technical details if simplified output is enabled
        if self._simplified_output:
            # Remove stack traces and debug information
            simplified = re.sub(r'Traceback.*?\n', '', simplified, flags=re.DOTALL)
            simplified = re.sub(r'File.*?line.*?\n', '', simplified)
            simplified = re.sub(r'\[.*?\]', '', simplified)  # Remove bracketed technical info
        
        return simplified.strip()