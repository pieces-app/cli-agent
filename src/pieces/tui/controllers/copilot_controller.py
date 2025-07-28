"""Controller for handling copilot operations and streaming."""

from typing import Optional, TYPE_CHECKING
from pieces.settings import Settings
from .base_controller import BaseController, EventType

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.qgpt_stream_output import (
        QGPTStreamOutput,
    )
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat


class CopilotController(BaseController):
    """Handles all copilot operations including streaming responses."""

    def __init__(self):
        """Initialize the copilot controller."""
        super().__init__()
        self._current_response = ""
        self._current_status: Optional[str] = None
        self._current_chat: Optional["BasicChat"] = None

    def initialize(self):
        """Initialize the copilot controller."""
        if self._initialized:
            return

        try:
            # Set up streaming callback
            if Settings.pieces_client.copilot.ask_stream_ws:
                Settings.pieces_client.copilot.ask_stream_ws.on_message_callback = (  # pyright: ignore[reportAttributeAccessIssue]
                    self._on_stream_message
                )

            self._initialized = True
            Settings.logger.info("CopilotController initialized")

        except Exception as e:
            Settings.logger.error(f"Failed to initialize CopilotController: {e}")

    def cleanup(self):
        """Clean up copilot resources."""
        self._current_response = ""
        self._current_status = None
        self._initialized = False

    def ask_question(self, query: str):
        """
        Ask a question to the copilot.

        Args:
            query: The question to ask
        """
        try:
            # Reset state
            self._current_response = ""
            self._current_status = None

            # Emit thinking started event
            self.emit(EventType.COPILOT_THINKING_STARTED, {"query": query})

            # Start streaming
            Settings.pieces_client.copilot.stream_question(query)

        except Exception as e:
            Settings.logger.error(f"Error asking question: {e}")
            self.emit(
                EventType.COPILOT_STREAM_ERROR,
                {
                    "error": str(e),
                    "partial_response": "",
                    "status": None,
                    "query": query,
                },
            )

    def _on_stream_message(self, response: "QGPTStreamOutput"):
        """Handle streaming messages from copilot."""
        try:
            current_status = response.status if response.status else "UNKNOWN"

            # Track status transitions
            if self._current_status != current_status:
                previous_status = self._current_status
                self._current_status = current_status

                # Handle status transitions
                if previous_status is None and current_status == "INITIALIZED":
                    self.emit(EventType.COPILOT_THINKING_ENDED, None)
                elif (
                    previous_status == "INITIALIZED" and current_status == "IN-PROGRESS"
                ):
                    # First actual content
                    pass

            # Handle response content
            if response.question and current_status == "IN-PROGRESS":
                answers = response.question.answers.iterable

                for answer in answers:
                    if answer.text:
                        if not self._current_response:
                            # First response chunk
                            self._current_response = answer.text
                            self.emit(
                                EventType.COPILOT_STREAM_STARTED,
                                {"text": self._current_response},
                            )
                        else:
                            # Subsequent chunks
                            self._current_response += answer.text
                            self.emit(
                                EventType.COPILOT_STREAM_CHUNK,
                                {
                                    "text": answer.text,
                                    "full_text": self._current_response,
                                },
                            )

            # Handle completion statuses
            if current_status == "COMPLETED":
                # Update chat state
                if response.conversation:
                    Settings.pieces_client.copilot.chat = BasicChat(
                        response.conversation
                    )

                # Emit completion event
                self.emit(
                    EventType.COPILOT_STREAM_COMPLETED,
                    {
                        "text": self._current_response,
                        "conversation": response.conversation,
                    },
                )

                # Reset state
                self._current_response = ""
                self._current_status = None

            elif current_status in ["FAILED", "STOPPED", "CANCELED"]:
                # Handle error/cancellation
                self.emit(
                    EventType.COPILOT_STREAM_ERROR,
                    {
                        "error": f"Stream {current_status.lower()}",
                        "partial_response": self._current_response,
                        "status": current_status,
                        "query": None,
                    },
                )

                # Reset state
                self._current_response = ""
                self._current_status = None

        except Exception as e:
            Settings.logger.error(f"Error handling stream message: {e}")
            self.emit(
                EventType.COPILOT_STREAM_ERROR,
                {
                    "error": str(e),
                    "partial_response": self._current_response,
                    "status": None,
                    "query": None,
                },
            )
            self._current_response = ""
            self._current_status = None

    def stop_streaming(self):
        """Stop the current streaming operation."""
        try:
            # Send stop signal if currently streaming
            if self.is_streaming() and Settings.pieces_client.copilot.ask_stream_ws:
                # Import here to avoid circular imports at module level
                from pieces._vendor.pieces_os_client.models.qgpt_stream_input import (
                    QGPTStreamInput,
                )

                # Send stop message
                stop_input = QGPTStreamInput(
                    conversation=Settings.pieces_client.copilot._chat_id, stop=True
                )
                Settings.pieces_client.copilot.ask_stream_ws.send_message(stop_input)

                # Emit stream stopped event
                self.emit(
                    EventType.COPILOT_STREAM_ERROR,
                    {
                        "error": "Stream stopped by user",
                        "partial_response": self._current_response,
                        "status": "STOPPED",
                        "query": None,
                    },
                )

            # Reset state
            self._current_response = ""
            self._current_status = None

        except Exception as e:
            Settings.logger.error(f"Error stopping stream: {e}")

    def is_streaming(self) -> bool:
        """Check if currently streaming a response."""
        return self._current_status == "IN-PROGRESS"

    def get_current_chat(self) -> Optional["BasicChat"]:
        """Get the current active chat."""
        return Settings.pieces_client.copilot.chat if Settings.pieces_client else None
