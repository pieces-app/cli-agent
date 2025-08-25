"""Textual messages for the TUI application."""

from typing import Optional, TYPE_CHECKING
from textual.message import Message

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.summary import (
        BasicSummary,
    )
    from pieces.config.schemas.model import ModelInfo


class ChatMessages:
    """Chat-related messages."""

    class Switched(Message):
        """Chat was switched to."""

        def __init__(self, chat: "BasicChat") -> None:
            super().__init__()
            self.chat = chat

    class NewRequested(Message):
        """New chat was requested."""

        pass

    class Updated(Message):
        """Chat was updated."""

        def __init__(self, chat: "BasicChat") -> None:
            super().__init__()
            self.chat = chat

    class Deleted(Message):
        """Chat was deleted."""

        def __init__(self, chat_id: str) -> None:
            super().__init__()
            self.chat_id = chat_id


class WorkstreamMessages:
    """Workstream-related messages."""

    class Switched(Message):
        """Workstream summary was switched to."""

        def __init__(self, summary: "BasicSummary") -> None:
            super().__init__()
            self.summary = summary

    class Updated(Message):
        """Workstream summary was updated."""

        def __init__(self, summary: "BasicSummary") -> None:
            super().__init__()
            self.summary = summary

    class Deleted(Message):
        """Workstream summary was deleted."""

        def __init__(self, summary_id: str) -> None:
            super().__init__()
            self.summary_id = summary_id

    class EditModeToggled(Message):
        """Edit mode was toggled for workstream content."""

        def __init__(self, edit_mode: bool) -> None:
            super().__init__()
            self.edit_mode = edit_mode

    class ContentSaved(Message):
        """Workstream content was saved."""

        def __init__(self, content: str) -> None:
            super().__init__()
            self.content = content

    class SwitchRequested(Message):
        """Workstream summary switch was requested (may need confirmation)."""

        def __init__(self, summary: "BasicSummary") -> None:
            super().__init__()
            self.summary = summary

    class SwitchConfirmed(Message):
        """Workstream summary switch was confirmed after unsaved changes check."""

        def __init__(self, summary: "BasicSummary") -> None:
            super().__init__()
            self.summary = summary


class UserMessages:
    """User input messages."""

    class InputSubmitted(Message):
        """User submitted input."""

        def __init__(self, text: str, timestamp: Optional[str] = None) -> None:
            super().__init__()
            self.text = text
            self.timestamp = timestamp


class ModelMessages:
    """Model-related messages."""

    class Changed(Message):
        """Model was changed."""

        def __init__(self, new_model: "ModelInfo") -> None:
            super().__init__()
            self.new_model = new_model


class ConnectionMessages:
    """Connection-related messages."""

    class Established(Message):
        """Connection was established."""

        def __init__(self) -> None:
            super().__init__()

    class Lost(Message):
        """Connection was lost."""

        def __init__(self) -> None:
            super().__init__()

    class Reconnecting(Message):
        """Connection is reconnecting."""

        pass


class CopilotMessages:
    """Copilot interaction messages."""

    class ThinkingStarted(Message):
        """Copilot started thinking."""

        def __init__(self) -> None:
            super().__init__()

    class ThinkingEnded(Message):
        """Copilot finished thinking."""

        pass

    class StreamStarted(Message):
        """Copilot started streaming response."""

        def __init__(self, text: str) -> None:
            super().__init__()
            self.text = text

    class StreamChunk(Message):
        """Copilot streamed a chunk."""

        def __init__(self, chunk: str, full_text: str) -> None:
            super().__init__()
            self.chunk = chunk
            self.full_text = full_text

    class StreamCompleted(Message):
        """Copilot completed streaming."""

        def __init__(self, final_text: str) -> None:
            super().__init__()
            self.final_text = final_text

    class StreamError(Message):
        """Copilot stream encountered an error."""

        def __init__(self, error: str) -> None:
            super().__init__()
            self.error = error


class ContextMessages:
    """Context-related messages."""

    class Added(Message):
        """Context was added."""

        def __init__(self, context_type: str, context_data: str) -> None:
            super().__init__()
            self.context_type = context_type
            self.context_data = context_data

    class Removed(Message):
        """Context was removed."""

        def __init__(self, context_type: str, context_data: str) -> None:
            super().__init__()
            self.context_type = context_type
            self.context_data = context_data

    class Cleared(Message):
        """All context was cleared."""

        def __init__(self, count: int) -> None:
            super().__init__()
            self.count = count


class ViewMessages:
    """View navigation messages."""

    class SwitchToChat(Message):
        """Switch to chat view."""

        pass

    class SwitchToWorkstream(Message):
        """Switch to workstream view."""

        pass

