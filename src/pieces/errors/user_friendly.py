"""
User-friendly error messages for Pieces CLI.

This module transforms technical error messages into helpful, actionable
messages that guide users toward solutions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Type, Callable
import re
import socket


class ErrorCategory(Enum):
    """Categories of errors for classification."""
    
    CONNECTION = "connection"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    VERSION = "version"
    CONFIGURATION = "configuration"
    RATE_LIMIT = "rate_limit"
    SERVER = "server"
    UNKNOWN = "unknown"


@dataclass
class UserFriendlyError:
    """
    Represents a user-friendly error message with context and solutions.
    
    Attributes:
        title: A brief description of what went wrong
        reasons: Possible reasons for the error
        solutions: Steps the user can try to resolve the issue
        help_link: URL to documentation or troubleshooting guide
        category: The category of error for classification
        original_error: The original exception that was caught
        technical_details: Optional technical details for debugging
    """
    
    title: str
    reasons: List[str] = field(default_factory=list)
    solutions: List[str] = field(default_factory=list)
    help_link: Optional[str] = None
    category: ErrorCategory = ErrorCategory.UNKNOWN
    original_error: Optional[Exception] = None
    technical_details: Optional[str] = None
    
    def format_error(self, include_technical: bool = False) -> str:
        """
        Format the error into a user-friendly string.
        
        Args:
            include_technical: Whether to include technical details
            
        Returns:
            A formatted error message string
        """
        lines = []
        
        # Title with error indicator
        lines.append(f"❌ {self.title}")
        lines.append("")
        
        # Possible reasons
        if self.reasons:
            lines.append("Possible reasons:")
            for reason in self.reasons:
                lines.append(f"  • {reason}")
            lines.append("")
        
        # Solutions
        if self.solutions:
            lines.append("Try these solutions:")
            for i, solution in enumerate(self.solutions, 1):
                lines.append(f"  {i}. {solution}")
            lines.append("")
        
        # Help link
        if self.help_link:
            lines.append(f"📖 More help: {self.help_link}")
        
        # Technical details (optional, for debugging)
        if include_technical and self.technical_details:
            lines.append("")
            lines.append(f"Technical details: {self.technical_details}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return self.format_error()


# Error patterns and their corresponding user-friendly messages
ERROR_PATTERNS: Dict[str, Dict] = {
    # Connection errors
    r"Connection refused|ConnectionRefusedError|\[Errno 61\]|\[Errno 111\]|\[WinError 10061\]": {
        "title": "Cannot connect to Pieces OS",
        "reasons": [
            "Pieces OS may not be running",
            "Pieces OS may be starting up",
            "The service port may be blocked",
        ],
        "solutions": [
            "Ensure Pieces OS is running: `pieces open`",
            "Check if Pieces OS is starting: `pieces status`",
            "Restart Pieces OS: `pieces restart`",
        ],
        "help_link": "https://docs.pieces.app/products/cli/troubleshooting",
        "category": ErrorCategory.CONNECTION,
    },
    
    r"WebSocket.*failed|WebSocket.*error|WebSocketException|WebSocketConnectionClosedException": {
        "title": "WebSocket connection failed",
        "reasons": [
            "Pieces OS may not be running",
            "Network connection issues",
            "Firewall blocking the connection",
        ],
        "solutions": [
            "Ensure Pieces OS is running: `pieces open`",
            "Check your network connection",
            "Try restarting Pieces OS: `pieces restart`",
        ],
        "help_link": "https://docs.pieces.app/products/cli/troubleshooting",
        "category": ErrorCategory.CONNECTION,
    },
    
    r"timeout|TimeoutError|timed out|ETIMEDOUT": {
        "title": "Operation timed out",
        "reasons": [
            "Pieces OS is taking too long to respond",
            "Network connection is slow or unstable",
            "The operation is processing a large amount of data",
        ],
        "solutions": [
            "Wait a moment and try again",
            "Check your network connection",
            "Restart Pieces OS: `pieces restart`",
        ],
        "help_link": "https://docs.pieces.app/products/cli/troubleshooting",
        "category": ErrorCategory.TIMEOUT,
    },
    
    r"MaxRetryError|Max retries exceeded|ConnectionError": {
        "title": "Cannot reach Pieces OS",
        "reasons": [
            "Pieces OS may not be running",
            "Too many failed connection attempts",
            "Network issues preventing connection",
        ],
        "solutions": [
            "Start Pieces OS: `pieces open`",
            "Check if Pieces OS is running: `pieces status`",
            "Check your network connection",
        ],
        "help_link": "https://docs.pieces.app/products/cli/troubleshooting",
        "category": ErrorCategory.CONNECTION,
    },
    
    # Authentication errors
    r"401|Unauthorized|authentication failed|invalid.*token|UnauthorizedException": {
        "title": "Authentication failed",
        "reasons": [
            "You may not be signed in",
            "Your session may have expired",
            "Invalid credentials",
        ],
        "solutions": [
            "Sign in to Pieces: `pieces login`",
            "If already signed in, try signing out and back in: `pieces logout` then `pieces login`",
        ],
        "help_link": "https://docs.pieces.app/products/cli/commands#login",
        "category": ErrorCategory.AUTHENTICATION,
    },
    
    r"403|Forbidden|ForbiddenException|access denied|permission denied": {
        "title": "Access denied",
        "reasons": [
            "You don't have permission for this operation",
            "The resource may be restricted",
            "Your account may have limitations",
        ],
        "solutions": [
            "Verify you're signed in with the correct account: `pieces login`",
            "Check if you have the necessary permissions",
        ],
        "help_link": "https://docs.pieces.app/products/cli/commands#login",
        "category": ErrorCategory.PERMISSION,
    },
    
    # Not found errors
    r"404|Not Found|NotFoundException|does not exist|not found": {
        "title": "Resource not found",
        "reasons": [
            "The requested item may have been deleted",
            "The item ID or name may be incorrect",
            "The resource may not exist yet",
        ],
        "solutions": [
            "Verify the item exists: `pieces list`",
            "Check the spelling of the item name or ID",
            "Create the resource if it doesn't exist",
        ],
        "help_link": "https://docs.pieces.app/products/cli/commands#list",
        "category": ErrorCategory.NOT_FOUND,
    },
    
    # Version compatibility errors
    r"version.*incompatible|update.*required|too old|CLI.*update|PiecesOS.*update": {
        "title": "Version compatibility issue",
        "reasons": [
            "Your Pieces CLI version may be outdated",
            "Your Pieces OS version may need updating",
            "Version mismatch between CLI and Pieces OS",
        ],
        "solutions": [
            "Update Pieces CLI: `pip install --upgrade pieces-cli`",
            "Update Pieces OS from https://pieces.app",
            "Check versions: `pieces version`",
        ],
        "help_link": "https://docs.pieces.app/products/meet-pieces/fundamentals",
        "category": ErrorCategory.VERSION,
    },
    
    # Rate limit errors
    r"429|rate limit|too many requests|quota exceeded": {
        "title": "Rate limit exceeded",
        "reasons": [
            "Too many requests in a short time",
            "API quota has been reached",
        ],
        "solutions": [
            "Wait a few moments before trying again",
            "Reduce the frequency of requests",
        ],
        "help_link": "https://docs.pieces.app/products/cli/troubleshooting",
        "category": ErrorCategory.RATE_LIMIT,
    },
    
    # Server errors
    r"500|502|503|504|Internal Server Error|ServiceException|server error": {
        "title": "Server error",
        "reasons": [
            "Pieces OS encountered an internal error",
            "The service may be temporarily unavailable",
            "Server overload",
        ],
        "solutions": [
            "Wait a moment and try again",
            "Restart Pieces OS: `pieces restart`",
            "Check Pieces status at https://status.pieces.app",
        ],
        "help_link": "https://docs.pieces.app/products/cli/troubleshooting",
        "category": ErrorCategory.SERVER,
    },
    
    # Permission/File system errors
    r"PermissionError|Permission denied|EACCES|access is denied": {
        "title": "Permission denied",
        "reasons": [
            "Insufficient file system permissions",
            "The file or directory may be protected",
            "Another process may be using the file",
        ],
        "solutions": [
            "Check file/folder permissions",
            "Run with appropriate permissions",
            "Close other applications that may be using the file",
        ],
        "help_link": "https://docs.pieces.app/products/cli/troubleshooting",
        "category": ErrorCategory.PERMISSION,
    },
    
    # Configuration errors
    r"config.*error|invalid.*config|configuration.*failed|FileNotFoundError.*config": {
        "title": "Configuration error",
        "reasons": [
            "Configuration file may be missing or corrupted",
            "Invalid configuration values",
            "Configuration file permissions issue",
        ],
        "solutions": [
            "Reset configuration: `pieces config --reset`",
            "Check configuration: `pieces config --show`",
            "Verify configuration file permissions",
        ],
        "help_link": "https://docs.pieces.app/products/cli/configuration",
        "category": ErrorCategory.CONFIGURATION,
    },
    
    # MCP specific errors
    r"MCP.*failed|MCP.*error|mcp.*not.*running": {
        "title": "MCP server error",
        "reasons": [
            "MCP server may not be running",
            "MCP configuration may be incorrect",
            "Connection to MCP server failed",
        ],
        "solutions": [
            "Start MCP server: `pieces mcp start`",
            "Check MCP status: `pieces mcp status`",
            "Repair MCP configuration: `pieces mcp repair`",
        ],
        "help_link": "https://docs.pieces.app/products/cli/copilot/chat#pieces-mcp",
        "category": ErrorCategory.CONNECTION,
    },
    
    # Git/Commit errors
    r"git.*error|not a git repository|commit.*failed": {
        "title": "Git operation failed",
        "reasons": [
            "Not in a git repository",
            "Git is not installed or not in PATH",
            "No changes to commit",
        ],
        "solutions": [
            "Ensure you're in a git repository",
            "Initialize a git repository: `git init`",
            "Check if there are changes to commit: `git status`",
        ],
        "help_link": "https://docs.pieces.app/products/cli/commands#commit",
        "category": ErrorCategory.CONFIGURATION,
    },
}


def _match_error_pattern(error_message: str) -> Optional[Dict]:
    """
    Match an error message against known patterns.
    
    Args:
        error_message: The error message to match
        
    Returns:
        The matching error configuration or None
    """
    for pattern, config in ERROR_PATTERNS.items():
        if re.search(pattern, error_message, re.IGNORECASE):
            return config
    return None


def get_user_friendly_message(
    exception: Exception,
    default_help_link: str = "https://docs.pieces.app/products/cli/troubleshooting",
) -> UserFriendlyError:
    """
    Transform an exception into a user-friendly error message.
    
    Args:
        exception: The exception to transform
        default_help_link: Default help URL if no specific one is found
        
    Returns:
        A UserFriendlyError with helpful information
    """
    error_message = str(exception)
    exception_type = type(exception).__name__
    
    # Combine exception type and message for matching
    full_error = f"{exception_type}: {error_message}"
    
    # Try to match against known patterns
    config = _match_error_pattern(full_error)
    
    if config:
        return UserFriendlyError(
            title=config["title"],
            reasons=config.get("reasons", []),
            solutions=config.get("solutions", []),
            help_link=config.get("help_link", default_help_link),
            category=config.get("category", ErrorCategory.UNKNOWN),
            original_error=exception,
            technical_details=full_error,
        )
    
    # Handle specific exception types that might not match patterns
    if isinstance(exception, ConnectionRefusedError) or (
        isinstance(exception, OSError) and exception.errno in (61, 111, 10061)
    ):
        return UserFriendlyError(
            title="Cannot connect to Pieces OS",
            reasons=[
                "Pieces OS may not be running",
                "The service port may be blocked",
            ],
            solutions=[
                "Ensure Pieces OS is running: `pieces open`",
                "Restart Pieces OS: `pieces restart`",
            ],
            help_link="https://docs.pieces.app/products/cli/troubleshooting",
            category=ErrorCategory.CONNECTION,
            original_error=exception,
            technical_details=full_error,
        )
    
    if isinstance(exception, TimeoutError) or isinstance(exception, socket.timeout):
        return UserFriendlyError(
            title="Operation timed out",
            reasons=[
                "The operation took too long to complete",
                "Network connection may be slow",
            ],
            solutions=[
                "Try again in a moment",
                "Check your network connection",
                "Restart Pieces OS: `pieces restart`",
            ],
            help_link="https://docs.pieces.app/products/cli/troubleshooting",
            category=ErrorCategory.TIMEOUT,
            original_error=exception,
            technical_details=full_error,
        )
    
    if isinstance(exception, PermissionError):
        return UserFriendlyError(
            title="Permission denied",
            reasons=[
                "Insufficient file system permissions",
                "The file or directory may be protected",
            ],
            solutions=[
                "Check file/folder permissions",
                "Run with appropriate permissions",
            ],
            help_link="https://docs.pieces.app/products/cli/troubleshooting",
            category=ErrorCategory.PERMISSION,
            original_error=exception,
            technical_details=full_error,
        )
    
    if isinstance(exception, FileNotFoundError):
        return UserFriendlyError(
            title="File not found",
            reasons=[
                "The specified file does not exist",
                "The file path may be incorrect",
            ],
            solutions=[
                "Verify the file path is correct",
                "Check if the file exists",
            ],
            help_link="https://docs.pieces.app/products/cli/troubleshooting",
            category=ErrorCategory.NOT_FOUND,
            original_error=exception,
            technical_details=full_error,
        )
    
    # Default fallback for unknown errors
    return UserFriendlyError(
        title="An unexpected error occurred",
        reasons=[
            "An internal error occurred",
            "This may be a temporary issue",
        ],
        solutions=[
            "Try again in a moment",
            "Restart Pieces OS: `pieces restart`",
            "If the problem persists, report it: `pieces feedback`",
        ],
        help_link=default_help_link,
        category=ErrorCategory.UNKNOWN,
        original_error=exception,
        technical_details=full_error,
    )


def format_error(
    exception: Exception,
    include_technical: bool = False,
    default_help_link: str = "https://docs.pieces.app/products/cli/troubleshooting",
) -> str:
    """
    Format an exception into a user-friendly error string.
    
    This is a convenience function that combines get_user_friendly_message
    and UserFriendlyError.format_error.
    
    Args:
        exception: The exception to format
        include_technical: Whether to include technical details
        default_help_link: Default help URL if no specific one is found
        
    Returns:
        A formatted error message string
    """
    friendly_error = get_user_friendly_message(exception, default_help_link)
    return friendly_error.format_error(include_technical)


# Exception type to handler mapping for direct type-based lookups
EXCEPTION_HANDLERS: Dict[Type[Exception], Callable[[Exception], UserFriendlyError]] = {}


def register_exception_handler(
    exception_type: Type[Exception],
) -> Callable[[Callable[[Exception], UserFriendlyError]], Callable[[Exception], UserFriendlyError]]:
    """
    Decorator to register a custom handler for a specific exception type.
    
    Usage:
        @register_exception_handler(MyCustomException)
        def handle_my_exception(e: MyCustomException) -> UserFriendlyError:
            return UserFriendlyError(
                title="My custom error",
                reasons=["Custom reason"],
                solutions=["Custom solution"],
            )
    """
    def decorator(handler: Callable[[Exception], UserFriendlyError]) -> Callable[[Exception], UserFriendlyError]:
        EXCEPTION_HANDLERS[exception_type] = handler
        return handler
    return decorator
