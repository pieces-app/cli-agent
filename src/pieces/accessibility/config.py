"""
Accessibility configuration for Pieces CLI.

Handles detection of user accessibility preferences including:
- NO_COLOR environment variable support
- System color scheme detection
- High contrast mode detection
- Screen reader mode detection
- Verbose output mode for accessibility
- Keyboard navigation preferences
- Cognitive accessibility preferences
"""

import os
import sys
from enum import Enum
from typing import Optional


class ColorScheme(Enum):
    """Accessible color schemes following accessibility standards."""
    DEFAULT = "default"
    HIGH_CONTRAST = "high_contrast"
    MONOCHROME = "monochrome"
    DEUTERANOPIA = "deuteranopia"  # Red-green colorblind
    PROTANOPIA = "protanopia"      # Red-green colorblind
    TRITANOPIA = "tritanopia"      # Blue-yellow colorblind


class AccessibilityConfig:
    """
    Manages accessibility configuration and preference detection.
    
    Follows standards from:
    - NO_COLOR: https://no-color.org/
    - WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
    """
    
    def __init__(self):
        self._color_scheme = self._detect_color_scheme()
        self._no_color = self._check_no_color()
        self._high_contrast = self._check_high_contrast()
        self._screen_reader = self._check_screen_reader()
        self._verbose = self._check_verbose_mode()
        self._keyboard_navigation = self._check_keyboard_navigation()
        self._reduced_motion = self._check_reduced_motion()
        self._simplified_output = self._check_simplified_output()
        self._clear_language = self._check_clear_language()
        
    @property
    def color_scheme(self) -> ColorScheme:
        """Get the detected color scheme."""
        return self._color_scheme
    
    @property
    def no_color(self) -> bool:
        """Check if NO_COLOR is enabled."""
        return self._no_color
    
    @property
    def high_contrast(self) -> bool:
        """Check if high contrast mode is enabled."""
        return self._high_contrast
    
    @property
    def should_use_color(self) -> bool:
        """Determine if colors should be used based on preferences."""
        return not self._no_color
    
    @property
    def screen_reader(self) -> bool:
        """Check if screen reader mode is enabled."""
        return self._screen_reader
    
    @property
    def verbose(self) -> bool:
        """Check if verbose mode is enabled for accessibility."""
        return self._verbose
    
    @property
    def keyboard_navigation(self) -> bool:
        """Check if keyboard navigation mode is enabled."""
        return self._keyboard_navigation
    
    @property
    def reduced_motion(self) -> bool:
        """Check if reduced motion preference is enabled."""
        return self._reduced_motion
    
    @property
    def simplified_output(self) -> bool:
        """Check if simplified output mode is enabled."""
        return self._simplified_output
    
    @property
    def clear_language(self) -> bool:
        """Check if clear language mode is enabled."""
        return self._clear_language
    
    def _detect_color_scheme(self) -> ColorScheme:
        """
        Detect user's preferred color scheme from environment and system settings.
        
        Priority order:
        1. NO_COLOR environment variable (forces monochrome - highest priority)
        2. PIECES_COLOR_SCHEME environment variable
        3. System high contrast mode
        4. Default
        """
        # Check NO_COLOR standard first (highest priority)
        if self._check_no_color():
            return ColorScheme.MONOCHROME
        
        # Check explicit environment variable
        env_scheme = os.environ.get('PIECES_COLOR_SCHEME')
        if env_scheme:
            try:
                return ColorScheme(env_scheme.lower())
            except ValueError:
                pass  # Invalid scheme, continue detection
        
        # Check system high contrast
        if self._check_high_contrast():
            return ColorScheme.HIGH_CONTRAST
        
        return ColorScheme.DEFAULT
    
    def _check_no_color(self) -> bool:
        """
        Check for NO_COLOR environment variable.
        
        Following the standard from https://no-color.org/
        Command-line software which outputs colored text should check for the presence
        of this environment variable. When present (regardless of its value), the software
        should suppress color output.
        """
        return 'NO_COLOR' in os.environ
    
    def _check_high_contrast(self) -> bool:
        """
        Check if system high contrast mode is enabled.
        
        Currently supports Windows high contrast detection.
        Can be extended for other platforms.
        """
        if sys.platform == 'win32':
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r'Control Panel\Accessibility\HighContrast'
                )
                flags = winreg.QueryValueEx(key, 'Flags')[0]
                # HCF_HIGHCONTRASTON = 0x01
                if flags & 1:
                    return True
            except (OSError, ImportError):
                pass
        
        return False
    
    def _check_screen_reader(self) -> bool:
        """
        Check if screen reader mode should be enabled.
        
        Detects screen reader through:
        1. PIECES_SCREEN_READER environment variable
        2. Common screen reader environment variables
        3. Screen reader detection on different platforms
        """
        # Check explicit environment variable
        if 'PIECES_SCREEN_READER' in os.environ:
            return os.environ['PIECES_SCREEN_READER'].lower() in ('1', 'true', 'yes', 'on')
        
        # Check common screen reader environment variables
        screen_reader_vars = [
            'SCREEN_READER',           # Generic
            'JAWS',                    # JAWS for Windows
            'NVDA',                    # NVDA for Windows
            'ORCA',                    # Orca for Linux
            'VOICEOVER',               # VoiceOver for macOS
            'TALKBACK',                # TalkBack for Android
            'TERMINAL_SCREEN_READER'  # Terminal screen readers
        ]
        
        for var in screen_reader_vars:
            if var in os.environ:
                return True
        
        # Platform-specific detection
        if sys.platform == 'win32':
            try:
                import winreg
                # Check for common screen readers in Windows registry
                screen_readers = [
                    r'SOFTWARE\Freedom Scientific\JAWS',
                    r'SOFTWARE\NVDA',
                    r'SOFTWARE\Microsoft\Windows NT\CurrentVersion\Accessibility'
                ]
                for sr_path in screen_readers:
                    try:
                        winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, sr_path)
                        return True
                    except OSError:
                        continue
            except (OSError, ImportError):
                pass
        elif sys.platform == 'darwin':
            # Check for VoiceOver on macOS
            try:
                import subprocess
                result = subprocess.run(
                    ['defaults', 'read', 'com.apple.universalaccess', 'voiceOverOn'],
                    capture_output=True, text=True, timeout=1
                )
                if result.stdout.strip() == '1':
                    return True
            except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
        elif sys.platform.startswith('linux'):
            # Check for Orca or other Linux screen readers
            try:
                import subprocess
                # Check if Orca is running
                result = subprocess.run(
                    ['pgrep', '-x', 'orca'],
                    capture_output=True, timeout=1
                )
                if result.returncode == 0:
                    return True
            except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return False
    
    def _check_verbose_mode(self) -> bool:
        """
        Check if verbose mode should be enabled for accessibility.
        
        Verbose mode provides more descriptive output that's helpful for screen readers.
        """
        # Check explicit environment variable
        if 'PIECES_VERBOSE' in os.environ:
            return os.environ['PIECES_VERBOSE'].lower() in ('1', 'true', 'yes', 'on')
        
        # Auto-enable verbose mode when screen reader is detected
        if self._screen_reader:
            return True
        
        return False
    
    def _check_keyboard_navigation(self) -> bool:
        """
        Check if keyboard navigation mode should be enabled.
        
        Detects keyboard navigation preferences through:
        1. PIECES_KEYBOARD_NAVIGATION environment variable
        2. System keyboard navigation settings
        """
        # Check explicit environment variable
        if 'PIECES_KEYBOARD_NAVIGATION' in os.environ:
            return os.environ['PIECES_KEYBOARD_NAVIGATION'].lower() in ('1', 'true', 'yes', 'on')
        
        # Auto-enable when screen reader is active (screen reader users typically use keyboard)
        if self._screen_reader:
            return True
        
        # Check system keyboard navigation settings
        if sys.platform == 'win32':
            try:
                import winreg
                # Check Windows keyboard navigation settings
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r'Control Panel\Accessibility\Keyboard Preference'
                )
                try:
                    value = winreg.QueryValueEx(key, 'On')[0]
                    if value:
                        return True
                except OSError:
                    pass
            except (OSError, ImportError):
                pass
        elif sys.platform == 'darwin':
            # Check macOS keyboard navigation settings
            try:
                import subprocess
                result = subprocess.run(
                    ['defaults', 'read', 'com.apple.universalaccess', 'keyboardFullAccess'],
                    capture_output=True, text=True, timeout=1
                )
                if result.stdout.strip() == '1':
                    return True
            except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
        elif sys.platform.startswith('linux'):
            # Check Linux accessibility settings
            try:
                import subprocess
                # Check for assistive technologies
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.a11y.applications', 'screen-reader-enabled'],
                    capture_output=True, text=True, timeout=1
                )
                if 'true' in result.stdout.lower():
                    return True
            except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return False
    
    def _check_reduced_motion(self) -> bool:
        """
        Check if reduced motion preference is enabled.
        
        Reduces animations and transitions for users who prefer reduced motion.
        """
        # Check explicit environment variable
        if 'PIECES_REDUCED_MOTION' in os.environ:
            return os.environ['PIECES_REDUCED_MOTION'].lower() in ('1', 'true', 'yes', 'on')
        
        # Check system reduced motion settings
        if sys.platform == 'win32':
            try:
                import winreg
                # Check Windows reduced motion settings
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r'Control Panel\Accessibility\VisualEffects'
                )
                try:
                    value = winreg.QueryValueEx(key, 'VisualEffects')[0]
                    # 0 = Let Windows decide, 1 = Adjust for best performance, 2 = Custom
                    if value == 1:
                        return True
                except OSError:
                    pass
            except (OSError, ImportError):
                pass
        elif sys.platform == 'darwin':
            # Check macOS reduced motion settings
            try:
                import subprocess
                result = subprocess.run(
                    ['defaults', 'read', 'com.apple.universalaccess', 'reduceMotion'],
                    capture_output=True, text=True, timeout=1
                )
                if result.stdout.strip() == '1':
                    return True
            except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
        elif sys.platform.startswith('linux'):
            # Check Linux reduced motion settings
            try:
                import subprocess
                result = subprocess.run(
                    ['gsettings', 'get', 'org.gnome.desktop.interface', 'enable-animations'],
                    capture_output=True, text=True, timeout=1
                )
                if 'false' in result.stdout.lower():
                    return True
            except (OSError, subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return False
    
    def _check_simplified_output(self) -> bool:
        """
        Check if simplified output mode should be enabled.
        
        Simplified output reduces complexity and makes information easier to process.
        """
        # Check explicit environment variable
        if 'PIECES_SIMPLIFIED_OUTPUT' in os.environ:
            return os.environ['PIECES_SIMPLIFIED_OUTPUT'].lower() in ('1', 'true', 'yes', 'on')
        
        # Auto-enable with screen reader or verbose mode
        if self._screen_reader or self._verbose:
            return True
        
        return False
    
    def _check_clear_language(self) -> bool:
        """
        Check if clear language mode should be enabled.
        
        Clear language mode uses simpler words and provides more context.
        """
        # Check explicit environment variable
        if 'PIECES_CLEAR_LANGUAGE' in os.environ:
            return os.environ['PIECES_CLEAR_LANGUAGE'].lower() in ('1', 'true', 'yes', 'on')
        
        # Auto-enable with simplified output
        if self._simplified_output:
            return True
        
        return False
    
    def get_accessible_color(self, semantic_color: str) -> Optional[str]:
        """
        Get accessible color mapping for semantic colors.
        
        Args:
            semantic_color: Semantic color name (success, error, warning, info, muted)
            
        Returns:
            Color string for the current scheme, or None if no color should be used
        """
        if not self.should_use_color:
            return None
        
        color_map = {
            ColorScheme.DEFAULT: {
                'success': 'green',
                'error': 'red',
                'warning': 'yellow',
                'info': 'blue',
                'muted': 'dim'
            },
            ColorScheme.HIGH_CONTRAST: {
                'success': 'bright_white',
                'error': 'bright_yellow',
                'warning': 'bright_cyan',
                'info': 'bright_white',
                'muted': 'white'
            },
            ColorScheme.MONOCHROME: {
                # Use text decorations instead of colors
                'success': 'bold',
                'error': 'bold',
                'warning': 'underline',
                'info': 'default',
                'muted': 'dim'
            },
            ColorScheme.DEUTERANOPIA: {
                # Avoid red-green combinations for red-green colorblindness
                'success': 'blue',
                'error': 'bright_yellow',
                'warning': 'bright_cyan',
                'info': 'bright_blue',
                'muted': 'dim'
            },
            ColorScheme.PROTANOPIA: {
                # Avoid red-green combinations for red-green colorblindness
                'success': 'blue',
                'error': 'bright_yellow',
                'warning': 'bright_cyan',
                'info': 'bright_blue',
                'muted': 'dim'
            },
            ColorScheme.TRITANOPIA: {
                # Avoid blue-yellow combinations for blue-yellow colorblindness
                'success': 'green',
                'error': 'red',
                'warning': 'bright_magenta',
                'info': 'cyan',
                'muted': 'dim'
            }
        }
        
        scheme_colors = color_map.get(self._color_scheme, color_map[ColorScheme.DEFAULT])
        return scheme_colors.get(semantic_color)
    
    def get_text_indicator(self, semantic_color: str) -> str:
        """
        Get text-based indicators for semantic colors when color is not available.
        
        For screen readers, uses more descriptive text indicators.
        
        Args:
            semantic_color: Semantic color name
            
        Returns:
            Unicode character prefix or descriptive text for the semantic meaning
        """
        # Use descriptive text for screen readers
        if self._screen_reader:
            indicators = {
                'success': '[SUCCESS]',
                'error': '[ERROR]',
                'warning': '[WARNING]',
                'info': '[INFO]',
                'muted': ''
            }
            return indicators.get(semantic_color, '')
        
        # Use Unicode indicators when colors are disabled (not screen reader)
        if not self.should_use_color or self._color_scheme == ColorScheme.MONOCHROME:
            indicators = {
                'success': '✓',
                'error': '✗',
                'warning': '⚠',
                'info': 'ℹ',
                'muted': ''
            }
            return indicators.get(semantic_color, '')
        
        return ''
    
    def get_descriptive_prefix(self, semantic_color: str) -> str:
        """
        Get descriptive prefix for screen reader friendly output.
        
        Provides clear, spoken-friendly prefixes for different message types.
        
        Args:
            semantic_color: Semantic color name
            
        Returns:
            Descriptive text prefix for screen readers
        """
        if not self._screen_reader and not self._verbose:
            return ''
        
        descriptions = {
            'success': 'Success: ',
            'error': 'Error: ',
            'warning': 'Warning: ',
            'info': 'Information: ',
            'muted': ''
        }
        return descriptions.get(semantic_color, '')