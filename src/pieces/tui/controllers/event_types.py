"""Type-safe event definitions and data models for controllers."""

from typing import TypedDict, Optional, Any, NotRequired


class ContextEventData(TypedDict):
    """Data for context events."""

    type: str  # "material" or "file"
    item: Any
    total_count: int


class ContextClearedData(TypedDict):
    """Data for context cleared event."""

    type: str  # "materials" or "files"
    previous_count: int


class ConnectionEstablishedData(TypedDict):
    """Data for connection established event."""

    health: Any
    version: str


class ConnectionLostData(TypedDict, total=False):
    """Data for connection lost event."""

    error: Optional[str]


class CopilotThinkingData(TypedDict):
    """Data for copilot thinking started event."""

    query: str


class CopilotStreamStartedData(TypedDict):
    """Data for copilot stream started event."""

    text: str


class CopilotStreamChunkData(TypedDict):
    """Data for copilot stream chunk event."""

    text: str
    full_text: str


class CopilotStreamCompletedData(TypedDict):
    """Data for copilot stream completed event."""

    text: str
    conversation: Optional[str]


class CopilotStreamErrorData(TypedDict):
    """Data for copilot stream error event."""

    error: str
    partial_response: str
    status: NotRequired[Optional[str]]
    query: NotRequired[Optional[str]]
