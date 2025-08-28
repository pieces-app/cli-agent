"""Controller for handling copilot operations and streaming."""

from typing import Optional, TYPE_CHECKING
from pieces.settings import Settings
from .base_controller import BaseController, EventType
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.qgpt_stream_output import (
        QGPTStreamOutput,
    )


class CopilotController(BaseController):
    """Handles all copilot operations including streaming responses."""

    def __init__(self):
        """Initialize the copilot controller."""
        super().__init__()
        self._current_response = ""
        self._current_status: Optional[str] = None
        self._current_chat: Optional[BasicChat] = None

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
        try:
            # Clear streaming state
            self._current_response = ""
            self._current_status = None
            self._current_chat = None

        except Exception as e:
            Settings.logger.error(f"Error during copilot cleanup: {e}")

        # Clear all event listeners
        self._safe_cleanup()

    def ask_question(self, query: str):
        """
        Ask a question to the copilot.

        Args:
            query: The question to ask
        """
        self._current_response = ""
        self._current_status = None

        # Check if we need to create a new chat
        current_chat = Settings.pieces_client.copilot.chat
        if not current_chat:
            Settings.logger.info(
                "No active chat, copilot will create new one automatically"
            )

        # Emit thinking started event
        self.emit(EventType.COPILOT_THINKING_STARTED, None)

        # Start streaming - copilot will create chat automatically if needed
        Settings.pieces_client.copilot.stream_question(query)

    def _on_stream_message(self, response: "QGPTStreamOutput"):
        """Handle streaming messages from copilot."""
        try:
            current_status = response.status

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
                            # First chunk - start streaming
                            self._current_response = answer.text
                            self.emit(
                                EventType.COPILOT_STREAM_STARTED,
                                self._current_response,
                            )
                        else:
                            # Subsequent chunks - update accumulated response and emit chunk event
                            self._current_response += answer.text
                            self.emit(
                                EventType.COPILOT_STREAM_CHUNK,
                                {
                                    "text": answer.text,
                                    "full_text": self._current_response,
                                },
                            )

            elif current_status == "COMPLETED":
                if response.conversation:
                    new_chat = BasicChat(response.conversation)
                    old_chat = Settings.pieces_client.copilot.chat
                    Settings.pieces_client.copilot.chat = new_chat

                    # If this is a new chat (different from previous), emit chat switched event
                    if not old_chat or old_chat.id != new_chat.id:
                        Settings.logger.info(
                            f"Copilot created/switched to chat: {new_chat.id}"
                        )
                        # Emit event that event hub will bridge to CHAT_SWITCHED
                        self.emit(EventType.CHAT_SWITCHED, new_chat)

                # Emit completion event
                self.emit(
                    EventType.COPILOT_STREAM_COMPLETED,
                    self._current_response,
                )

                # Reset state
                self._current_response = ""
                self._current_status = None

            elif (
                current_status == "FAILED"
                or current_status == "STOPPED"
                or current_status == "CANCELED"
            ):
                # Handle error/cancellation
                self.emit(
                    EventType.COPILOT_STREAM_ERROR,
                    {
                        "error": f"Stream {response.error_message}",
                        "partial_response": self._current_response,
                        "status": current_status,
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
                    "status": "FAILED",
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
