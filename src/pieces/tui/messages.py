"""Textual messages for the TUI application."""

from typing import Optional, List, TYPE_CHECKING
from textual.message import Message

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.asset import (
        BasicAsset,
    )
    from pieces.config.schemas.model import ModelInfo


class ChatMessages:
    """Chat-related messages."""

    class Selected(Message):
        """Chat was selected."""

        def __init__(self, chat: "BasicChat") -> None:
            super().__init__()
            self.chat = chat

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

        def __init__(self, chat: "BasicChat") -> None:
            super().__init__()
            self.chat = chat


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

        def __init__(
            self, new_model: "ModelInfo", old_model: Optional["ModelInfo"] = None
        ) -> None:
            super().__init__()
            self.new_model = new_model
            self.old_model = old_model


class MaterialMessages:
    """Material/asset-related messages."""

    class Created(Message):
        """Material was created."""

        def __init__(self, asset: "BasicAsset") -> None:
            super().__init__()
            self.asset = asset

    class Updated(Message):
        """Material was updated."""

        def __init__(self, asset: "BasicAsset") -> None:
            super().__init__()
            self.asset = asset

    class Deleted(Message):
        """Material was deleted."""

        def __init__(self, asset: "BasicAsset") -> None:
            super().__init__()
            self.asset = asset

    class SearchCompleted(Message):
        """Material search completed."""

        def __init__(self, results: List["BasicAsset"]) -> None:
            super().__init__()
            self.results = results


class ConnectionMessages:
    """Connection-related messages."""

    class Established(Message):
        """Connection was established."""

        def __init__(self, endpoint: str) -> None:
            super().__init__()
            self.endpoint = endpoint

    class Lost(Message):
        """Connection was lost."""

        def __init__(self, reason: Optional[str] = None) -> None:
            super().__init__()
            self.reason = reason

    class Reconnecting(Message):
        """Connection is reconnecting."""

        pass


class CopilotMessages:
    """Copilot interaction messages."""

    class ThinkingStarted(Message):
        """Copilot started thinking."""

        def __init__(self, question: str) -> None:
            super().__init__()
            self.question = question

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

