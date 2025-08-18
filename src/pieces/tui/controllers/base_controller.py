"""Base controller for handling backend events."""

from typing import (
    Callable,
    Dict,
    List,
    Any,
    Optional,
    overload,
    Literal,
    TYPE_CHECKING,
)
from enum import Enum
from abc import ABC, abstractmethod
import threading
from pieces.config.schemas.model import ModelInfo
from pieces.settings import Settings
from .event_types import (
    ContextEventData,
    ContextClearedData,
    CopilotStreamChunkData,
    CopilotStreamErrorData,
)

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.asset import Asset
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.asset import (
        BasicAsset,
    )
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat


class EventType(Enum):
    """Event types that can be emitted by controllers."""

    # Chat events
    CHAT_UPDATED = "chat.updated"
    CHAT_DELETED = "chat.deleted"
    CHAT_SWITCHED = "chat.switched"

    # Model events
    MODEL_CHANGED = "model.changed"

    # Material events
    MATERIAL_CREATED = "material.created"
    MATERIAL_UPDATED = "material.updated"
    MATERIAL_DELETED = "material.deleted"
    MATERIALS_SEARCH_COMPLETED = "materials.search_completed"

    # Connection events
    CONNECTION_ESTABLISHED = "connection.established"
    CONNECTION_LOST = "connection.lost"
    CONNECTION_RECONNECTING = "connection.reconnecting"

    # Context events
    CONTEXT_ADDED = "context.added"
    CONTEXT_REMOVED = "context.removed"
    CONTEXT_CLEARED = "context.cleared"

    # Copilot events
    COPILOT_THINKING_STARTED = "copilot.thinking_started"
    COPILOT_THINKING_ENDED = "copilot.thinking_ended"
    COPILOT_STREAM_STARTED = "copilot.stream_started"
    COPILOT_STREAM_CHUNK = "copilot.stream_chunk"
    COPILOT_STREAM_COMPLETED = "copilot.stream_completed"
    COPILOT_STREAM_ERROR = "copilot.stream_error"


class BaseController(ABC):
    """Base controller class for handling backend events."""

    def __init__(self):
        """Initialize the base controller."""
        self._listeners: Dict[EventType, List[Callable]] = {}
        self._lock = threading.Lock()
        self._initialized = False

    @overload
    def on(
        self,
        event_type: Literal[EventType.CONNECTION_RECONNECTING],
        callback: Callable[[None], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.MODEL_CHANGED],
        callback: Callable[["ModelInfo"], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[
            EventType.MATERIAL_CREATED,
            EventType.MATERIAL_UPDATED,
            EventType.MATERIAL_DELETED,
        ],
        callback: Callable[["Asset"], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.MATERIALS_SEARCH_COMPLETED],
        callback: Callable[[List["BasicAsset"]], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.CONNECTION_ESTABLISHED],
        callback: Callable[[None], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.CHAT_UPDATED, EventType.CHAT_SWITCHED],
        callback: Callable[["BasicChat"], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.CHAT_DELETED],
        callback: Callable[[str], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.CONNECTION_LOST],
        callback: Callable[[None], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.CONTEXT_ADDED, EventType.CONTEXT_REMOVED],
        callback: Callable[[ContextEventData], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.CONTEXT_CLEARED],
        callback: Callable[[ContextClearedData], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.COPILOT_THINKING_STARTED],
        callback: Callable[[None], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.COPILOT_THINKING_ENDED],
        callback: Callable[[None], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_STARTED],
        callback: Callable[[str], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_CHUNK],
        callback: Callable[[CopilotStreamChunkData], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_COMPLETED],
        callback: Callable[[str], bool],
    ) -> None: ...
    @overload
    def on(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_ERROR],
        callback: Callable[[CopilotStreamErrorData], bool],
    ) -> None: ...

    # TODO: Add overloads for missing event types when models are ready:
    # - CHAT_SELECTED: needs BasicChat callback type
    # - CHAT_NEW_REQUESTED: needs None callback type

    def on(self, event_type: EventType, callback: Callable[[Any], bool]) -> None:
        """
        Register an event listener.

        Args:
            event_type: The type of event to listen for
            callback: Function to call when event occurs

        Returns:
            The callback function (for decorator usage)
        """
        with self._lock:
            if event_type not in self._listeners:
                self._listeners[event_type] = []
            self._listeners[event_type].append(callback)

    @overload
    def off(
        self,
        event_type: Literal[EventType.MODEL_CHANGED],
        callback: Callable[[Optional["ModelInfo"]], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[
            EventType.MATERIAL_CREATED,
            EventType.MATERIAL_UPDATED,
            EventType.MATERIAL_DELETED,
        ],
        callback: Callable[["Asset"], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.MATERIALS_SEARCH_COMPLETED],
        callback: Callable[[List["BasicAsset"]], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.CONNECTION_ESTABLISHED],
        callback: Callable[[None], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.CHAT_UPDATED, EventType.CHAT_SWITCHED],
        callback: Callable[["BasicChat"], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.CHAT_DELETED],
        callback: Callable[[str], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.CONNECTION_LOST],
        callback: Callable[[None], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.CONTEXT_ADDED, EventType.CONTEXT_REMOVED],
        callback: Callable[[ContextEventData], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.CONTEXT_CLEARED],
        callback: Callable[[ContextClearedData], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.COPILOT_THINKING_STARTED],
        callback: Callable[[None], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.COPILOT_THINKING_ENDED],
        callback: Callable[[None], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_STARTED],
        callback: Callable[[str], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_CHUNK],
        callback: Callable[[CopilotStreamChunkData], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_COMPLETED],
        callback: Callable[[str], bool],
    ) -> None: ...
    @overload
    def off(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_ERROR],
        callback: Callable[[CopilotStreamErrorData], bool],
    ) -> None: ...

    def off(self, event_type: EventType, callback: Callable[[Any], bool]):
        """
        Remove an event listener.

        Args:
            event_type: The type of event to stop listening for
            callback: The callback function to remove
        """
        with self._lock:
            if event_type in self._listeners:
                try:
                    self._listeners[event_type].remove(callback)
                except ValueError:
                    pass

    @overload
    def emit(
        self, event_type: Literal[EventType.MODEL_CHANGED], data: "ModelInfo"
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[
            EventType.MATERIAL_CREATED,
            EventType.MATERIAL_UPDATED,
            EventType.MATERIAL_DELETED,
        ],
        data: "Asset",
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.MATERIALS_SEARCH_COMPLETED],
        data: List["BasicAsset"],
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.CONNECTION_ESTABLISHED],
        data: None,
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.CHAT_UPDATED, EventType.CHAT_SWITCHED],
        data: "BasicChat",
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.CHAT_DELETED],
        data: str,
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.CONNECTION_LOST],
        data: None,
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.CONTEXT_ADDED, EventType.CONTEXT_REMOVED],
        data: ContextEventData,
    ) -> None: ...
    @overload
    def emit(
        self, event_type: Literal[EventType.CONTEXT_CLEARED], data: ContextClearedData
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.COPILOT_THINKING_STARTED],
        data: None,
    ) -> None: ...
    @overload
    def emit(
        self, event_type: Literal[EventType.COPILOT_THINKING_ENDED], data: None
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_STARTED],
        data: str,
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_CHUNK],
        data: CopilotStreamChunkData,
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.CONNECTION_RECONNECTING],
        data: None,
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_COMPLETED],
        data: str,
    ) -> None: ...
    @overload
    def emit(
        self,
        event_type: Literal[EventType.COPILOT_STREAM_ERROR],
        data: CopilotStreamErrorData,
    ) -> None: ...

    def emit(self, event_type: EventType, data: Optional[Any] = None):
        """
        Emit an event to all registered listeners.

        Args:
            event_type: The type of event to emit
            data: Optional data to pass to listeners
        """
        listeners = []
        with self._lock:
            if event_type in self._listeners:
                listeners = self._listeners[event_type].copy()

        for listener in listeners:
            try:
                listener(data)
            except Exception as e:
                Settings.logger.error(f"Error in event listener: {e}")

    def clear_listeners(self, event_type: Optional[EventType] = None):
        """
        Clear event listeners.

        Args:
            event_type: If provided, only clear listeners for this event type.
                       If None, clear all listeners.
        """
        with self._lock:
            if event_type:
                self._listeners.pop(event_type, None)
            else:
                self._listeners.clear()

    @abstractmethod
    def initialize(self):
        """Initialize the controller and set up event sources."""
        pass

    @abstractmethod
    def cleanup(self):
        """Clean up resources and stop listening to events."""
        pass

    def __del__(self):
        """Ensure cleanup is called when object is destroyed."""
        try:
            if self._initialized:
                self.cleanup()
        except (RuntimeError, ValueError, AttributeError):
            pass

    def _safe_cleanup(self):
        """Safely clean up base controller resources."""
        try:
            # Clear all event listeners
            self.clear_listeners()
            self._initialized = False
        except Exception as e:
            Settings.logger.error(f"Error during base controller cleanup: {e}")

    @property
    def is_initialized(self) -> bool:
        """Check if the controller is initialized."""
        return self._initialized
