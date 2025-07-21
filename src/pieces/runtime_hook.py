"""
Runtime hook for Pieces CLI PyInstaller build
This file is executed at runtime to provide legitimacy signals to antivirus software
"""

import sys
import os

# Set process description for Windows Task Manager
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("Pieces CLI - Developer Productivity Tool")
    except:
        pass

# Set environment variable to indicate legitimate application
os.environ['PIECES_CLI_LEGITIMATE'] = '1'

# Ensure proper console mode for Windows
if sys.platform == 'win32':
    # Enable ANSI color support
    os.system('') 