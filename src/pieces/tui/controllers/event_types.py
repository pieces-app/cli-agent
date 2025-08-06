"""Type-safe event definitions and data models for controllers."""

from typing import TypedDict, Any, Literal


class ContextEventData(TypedDict):
    """Data for context events."""

    type: str  # "material" or "file"
    item: Any
    total_count: int


class ContextClearedData(TypedDict):
    """Data for context cleared event."""

    type: str  # "materials" or "files"
    previous_count: int


class CopilotStreamChunkData(TypedDict):
    """Data for copilot stream chunk event."""

    text: str
    full_text: str


class CopilotStreamErrorData(TypedDict):
    """Data for copilot stream error event."""

    error: str
    partial_response: str
    status: Literal["FAILED", "STOPPED", "CANCELED"]
