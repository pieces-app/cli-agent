"""Copilot view - chat interface using base dual-pane architecture."""

from typing import Optional
from datetime import datetime

from textual.binding import Binding

from pieces.settings import Settings
from ..widgets import ChatViewPanel, ChatInput, ChatListPanel, StatusBar
from ..widgets.dialogs import ModelSelectionDialog, ConfirmDialog
from ..controllers import EventHub
from ..messages import (
    ChatMessages,
    UserMessages,
    ModelMessages,
    CopilotMessages,
    ContextMessages,
    ViewMessages,
)
from .base_dual_pane_view import BaseDualPaneView


class PiecesCopilot(BaseDualPaneView):
    """Copilot/chat interface with consistent dual-pane layout."""

    BINDINGS = [
        Binding("ctrl+n", "new_chat", "New Chat"),
        Binding("ctrl+shift+m", "change_model", "Change Model"),
        Binding("ctrl+l", "toggle_ltm", "Toggle LTM"),
        Binding("ctrl+shift+w", "switch_to_workstream", "Switch to Workstream"),
        Binding("ctrl+c", "stop_streaming", "Stop Streaming"),
    ]

    def __init__(self, event_hub: EventHub, **kwargs):
        super().__init__(event_hub=event_hub, view_name="Copilot", **kwargs)
        self.chat_view_panel: Optional[ChatViewPanel] = None
        self.chat_list_panel: Optional[ChatListPanel] = None
        self.chat_input: Optional[ChatInput] = None
        self.status_bar: Optional[StatusBar] = None

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool | None:
        """Check if an action may run."""
        is_streaming_active = (
            self.chat_view_panel and self.chat_view_panel.is_streaming_active()
        )
        if action == "stop_streaming" and not is_streaming_active:
            return False
        return True

    # Base view implementation
    def create_list_panel(self) -> ChatListPanel:
        """Create the chat list panel (LEFT side)."""
        self.chat_list_panel = ChatListPanel()
        return self.chat_list_panel

    def create_content_panel(self) -> ChatViewPanel:
        """Create the chat view panel (RIGHT side)."""
        self.chat_view_panel = ChatViewPanel()
        return self.chat_view_panel

    def create_additional_components(self):
        """Create chat input and status bar."""
        self.chat_input = ChatInput()
        yield self.chat_input

        self.status_bar = StatusBar()
        yield self.status_bar

    def _initialize_view(self):
        """Initialize chat-specific components."""
        # Model info
        current_model = self.event_hub.get_current_model()
        self._update_status_model(current_model)

        # Initialize LTM status
        if self.status_bar and self.event_hub:
            chat_ltm_enabled = self.event_hub.chat.is_chat_ltm_enabled()
            self.status_bar.update_ltm_status(chat_ltm_enabled)

        # Load items
        self._load_items()

        # Load current chat if exists
        current_chat = self.event_hub.get_current_chat()
        if current_chat and self.chat_view_panel:
            self.chat_view_panel.load_conversation(current_chat)
        else:
            if self.chat_view_panel:
                self.call_later(self._show_welcome_message)

    def _load_items(self):
        """Load chats into the list panel."""
        if not self.chat_list_panel or not self.event_hub:
            Settings.logger.info("Cannot load chats: missing components")
            return

        try:
            chats = Settings.pieces_client.copilot.chats()
            Settings.logger.info(f"Found {len(chats)} chats to load")
            self.chat_list_panel.load_chats(chats)

            # Set active chat if there's a current one
            current_chat = self.event_hub.get_current_chat()
            if current_chat:
                self.chat_list_panel.set_active_chat(current_chat)
                Settings.logger.info(f"Set active chat: {current_chat.name}")

        except Exception as e:
            Settings.logger.critical(f"Error loading chats: {e}")

    def _show_status_message(self, message: str, duration: int = 3):
        """Show temporary message in status bar."""
        if self.status_bar:
            self.status_bar.show_temporary_message(message, duration)

    # Chat-specific helper methods
    def _update_status_model(self, model_info):
        """Update model info in status bar."""
        if self.status_bar:
            self.status_bar.update_model_info(model_info)

    async def _show_welcome_message(self):
        """Show welcome message in chat view."""
        welcome_text = """🎯 Pieces Copilot

Type your message below to start chatting, or use these shortcuts:

• Ctrl+N - New conversation      • Ctrl+S - Toggle sidebar
• Ctrl+R - Refresh               • Ctrl+Shift+M - Change model
• Ctrl+L - Toggle LTM            • Ctrl+Shift+W - Workstream view

Ready to assist with code, questions, and more!"""

        if self.chat_view_panel:
            try:
                self.chat_view_panel._clear_content()
            except Exception:
                pass

            from textual.widgets import Static

            welcome_widget = Static(welcome_text, classes="welcome-message")
            self.chat_view_panel.mount(welcome_widget)

    # Message handlers that need view-level handling
    async def on_chat_messages_switched(self, message: ChatMessages.Switched) -> None:
        """Handle chat switch event - load conversation and focus input."""
        if self.chat_view_panel:
            Settings.logger.info(
                f"Updating conversation: {message.chat.id} - {message.chat.name}"
            )
            if message.chat:
                Settings.pieces_client.copilot.chat = message.chat
                # Check if we're in the middle of streaming - if so, don't reload yet
                has_streaming_widget = (
                    hasattr(self.chat_view_panel, "_streaming_widget")
                    and self.chat_view_panel._streaming_widget
                )
                has_thinking_widget = (
                    hasattr(self.chat_view_panel, "_thinking_widget")
                    and self.chat_view_panel._thinking_widget
                )

                if has_streaming_widget or has_thinking_widget:
                    Settings.logger.info(
                        "In middle of streaming/thinking, deferring conversation load"
                    )
                    self.chat_view_panel.border_title = f"Chat: {message.chat.name}"
                else:
                    # Normal case - load the full conversation
                    Settings.logger.info("Loading full conversation")
                    self.chat_view_panel.load_conversation(message.chat)
            else:
                # None chat means new chat - show welcome message
                self.chat_view_panel.clear_messages()
                self.chat_view_panel.border_title = "Chat: New Conversation"
                await self._show_welcome_message()

        if self.chat_input:
            self.chat_input.focus()

    async def on_chat_messages_new_requested(
        self, _: ChatMessages.NewRequested
    ) -> None:
        """Handle new chat request."""
        await self.action_new_chat()

    async def on_chat_messages_updated(self, message: ChatMessages.Updated) -> None:
        """Handle chat update event - update content if it's the active chat."""
        if not message.chat:
            return

        # If this is the active chat, update the view panel incrementally
        if (
            self.chat_view_panel
            and self.chat_list_panel
            and self.chat_list_panel.active_chat
            and self.chat_list_panel.active_chat.id == message.chat.id
        ):
            Settings.logger.info(
                f"Using incremental update for active chat: {message.chat.name}"
            )
            self.chat_view_panel.update_conversation_incrementally(message.chat)

    async def on_chat_messages_deleted(self, message: ChatMessages.Deleted) -> None:
        """Handle chat deletion event - clear view if it was the active chat."""
        active_chat_id = None
        try:
            if self.chat_list_panel and self.chat_list_panel.active_chat:
                active_chat_id = self.chat_list_panel.active_chat.id
        except (AttributeError, RuntimeError):
            pass

        # If this was the active chat, clear the view
        if active_chat_id == message.chat_id:
            if self.chat_view_panel:
                self.chat_view_panel.clear_messages()
                self.chat_view_panel.border_title = "Chat"
                await self._show_welcome_message()

    # Chat-specific message handlers
    async def on_user_messages_input_submitted(
        self, message: UserMessages.InputSubmitted
    ) -> None:
        """Handle user input submission."""
        Settings.logger.info(
            f"Copilot: User submitted question: {message.text[:50]}..."
        )
        if not self.event_hub:
            return

        # Check if streaming is active - don't process if it is
        if self.chat_view_panel and self.chat_view_panel.is_streaming_active():
            Settings.logger.info("Ignoring input submission - streaming is active")
            return

        # Remove welcome message and show user input immediately
        if self.chat_view_panel:
            try:
                # Clear any existing content (including welcome message)
                self.chat_view_panel._clear_content()
            except Exception:
                pass

            timestamp = datetime.now().strftime("Today %I:%M %p")
            self.chat_view_panel.add_message("user", message.text, timestamp=timestamp)
            self.chat_view_panel.increment_message_count()

        # Delegate to backend
        self.event_hub.ask_question(message.text)

    async def on_model_messages_changed(self, message: ModelMessages.Changed) -> None:
        """Handle model change."""
        self._update_status_model(message.new_model)
        self._show_status_message(f"🤖 Model changed to {message.new_model.name}")

    async def on_copilot_messages_thinking_started(
        self, _: CopilotMessages.ThinkingStarted
    ) -> None:
        """Handle copilot thinking started."""
        if self.chat_view_panel:
            self.chat_view_panel.add_thinking_indicator()

    async def on_copilot_messages_stream_started(
        self, message: CopilotMessages.StreamStarted
    ) -> None:
        """Handle copilot stream started."""
        if self.chat_view_panel:
            self.chat_view_panel.add_streaming_message("assistant", message.text)

    async def on_copilot_messages_stream_chunk(
        self, message: CopilotMessages.StreamChunk
    ) -> None:
        """Handle copilot stream chunk."""
        if self.chat_view_panel:
            self.chat_view_panel.update_streaming_message(message.full_text)

    async def on_copilot_messages_stream_completed(
        self, _: CopilotMessages.StreamCompleted
    ) -> None:
        """Handle copilot stream completion."""
        if self.chat_view_panel:
            self.chat_view_panel.finalize_streaming_message()

    async def on_copilot_messages_stream_error(
        self, message: CopilotMessages.StreamError
    ) -> None:
        """Handle copilot stream error."""
        if self.chat_view_panel:
            self.chat_view_panel.add_message("system", f"❌ Error: {message.error}")

    async def on_context_messages_cleared(
        self, message: ContextMessages.Cleared
    ) -> None:
        """Handle context cleared."""
        self._show_status_message(f"🗑️ Cleared {message.count} context items")

    # Chat-specific actions
    async def action_new_chat(self):
        """Request creation of a new chat."""
        if self.event_hub:
            self.event_hub.create_new_chat()

        if self.chat_input:
            self.chat_input.focus()

    def action_change_model(self):
        """Show model selection dialog and change the model."""
        if not self.event_hub:
            self._show_status_message("Unexpected error: Event hub not available")
            return

        try:
            models = self.event_hub.model.get_available_models()
            current_model = self.event_hub.get_current_model()
            current_model_name = current_model.name if current_model else None

            if not models:
                self._show_status_message("❌ No models available")
                return

            dialog = ModelSelectionDialog(models, current_model_name)
            self.app.push_screen(dialog, callback=self._handle_model_selection)

        except Exception as e:
            Settings.logger.error(f"Error in model selection: {e}")
            self._show_status_message("❌ Error changing model")

    def action_toggle_ltm(self):
        """Toggle LTM (Long Term Memory) for the current chat."""
        if not self.event_hub:
            self._show_status_message("Unexpected error: Event hub not available")
            return

        try:
            is_chat_ltm_enabled = self.event_hub.chat.is_chat_ltm_enabled()

            if is_chat_ltm_enabled:
                self.event_hub.chat.deactivate_ltm()
                self._show_status_message("🧠 Chat LTM disabled")
                if self.status_bar:
                    self.status_bar.update_ltm_status(False)
            else:
                is_system_ltm_running = self.event_hub.chat.is_ltm_running()

                if is_system_ltm_running:
                    self.event_hub.chat.activate_ltm()
                    self._show_status_message("🧠 Chat LTM enabled")
                    if self.status_bar:
                        self.status_bar.update_ltm_status(True)
                else:
                    self._show_ltm_setup_confirmation()

        except Exception as e:
            Settings.logger.error(f"Error in LTM toggle: {e}")
            self._show_status_message("❌ Error checking LTM status")

    def _show_ltm_setup_confirmation(self):
        """Show confirmation dialog for LTM setup."""
        dialog = ConfirmDialog(
            title="🧠 Long Term Memory Setup Required",
            message="To use LTM for this chat, you need to enable Pieces LTM first."
            "Would you like to open the LTM?",
        )
        self.app.push_screen(dialog, callback=self._handle_ltm_setup_confirmation)

    def _handle_ltm_setup_confirmation(self, confirmed):
        """Handle LTM setup confirmation result."""
        if confirmed:
            self._show_ltm_enable_dialog()
        else:
            self._show_status_message("❌ LTM setup cancelled")

    def _show_ltm_enable_dialog(self):
        """Show LTM enable dialog with TUI progress display."""
        import threading
        from pieces.copilot.ltm import check_ltm
        from pieces.tui.widgets.ltm_progress_dialog import LTMProgressDialog

        dialog = LTMProgressDialog()
        self.app.push_screen(dialog, callback=self._handle_ltm_enable_result)

        def run_ltm_enable():
            try:
                import time

                time.sleep(0.1)
                check_ltm(auto_enable=True, tui_dialog=dialog)
            except Exception as e:
                import traceback

                error_msg = f"❌ Error: {str(e)}\n{traceback.format_exc()}"
                dialog.set_complete(False, error_msg)

        thread = threading.Thread(target=run_ltm_enable, daemon=True)
        thread.start()

    def _handle_ltm_enable_result(self, success: bool | None) -> None:
        """Handle the result of LTM enable dialog."""
        if not self.event_hub:
            return
        if success:
            try:
                self.event_hub.chat.activate_ltm()
                self._show_status_message("🧠 LTM setup complete! Chat LTM enabled")
                if self.status_bar:
                    self.status_bar.update_ltm_status(True)
            except Exception as e:
                Settings.logger.error(f"Failed to enable chat LTM after setup: {e}")
                self._show_status_message("❌ Failed to enable chat LTM")
        elif success is False:
            self._show_status_message("❌ LTM setup cancelled")

    def _handle_model_selection(self, selected_model: str | None) -> None:
        """Handle the result of model selection dialog."""
        if not selected_model:
            return

        current_model = self.event_hub.get_current_model() if self.event_hub else None
        current_model_name = current_model.name if current_model else None

        if selected_model == current_model_name:
            self._show_status_message(f"🤖 Already using {selected_model}")
            return

        if self.event_hub:
            success = self.event_hub.model.change_model(selected_model)
            if success:
                Settings.logger.info(f"Successfully changed model to: {selected_model}")
            else:
                self._show_status_message("❌ Failed to change model")
        else:
            self._show_status_message("Something went wrong, please try again")

    def action_switch_to_workstream(self):
        """Switch to workstream view."""
        self.post_message(ViewMessages.SwitchToWorkstream())

    def action_stop_streaming(self):
        """Stop current streaming operation and clear streaming widgets."""
        if not self.event_hub:
            self._show_status_message("Unexpected error: Event hub not available")
            return

        try:
            # Check if streaming is active
            is_streaming_active = (
                self.chat_view_panel and self.chat_view_panel.is_streaming_active()
            )

            if is_streaming_active:
                # Stop the streaming operation
                self.event_hub.stop_streaming()

                # Clear streaming/thinking widgets
                if self.chat_view_panel:
                    self.chat_view_panel.clear_streaming_widget()
                    self.chat_view_panel._clear_thinking_indicator()

                self._show_status_message("🛑 Streaming stopped")
                Settings.logger.info("User stopped streaming with Ctrl+C")

        except Exception as e:
            Settings.logger.error(f"Error stopping streaming: {e}")
            self._show_status_message("❌ Error stopping streaming")

    def cleanup(self):
        """Clean up copilot view resources."""
        try:
            # Clear widget references
            self.chat_view_panel = None
            self.chat_list_panel = None
            self.chat_input = None
            self.status_bar = None

        except Exception as e:
            Settings.logger.error(f"Error during PiecesCopilot cleanup: {e}")

        super().cleanup()
