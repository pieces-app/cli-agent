"""Dialog widgets for the TUI application."""

from typing import List, Optional, TYPE_CHECKING
from textual.app import ComposeResult
from textual.widgets import Static, Button, Input, ListView, ListItem, Label
from textual.containers import Container, Horizontal
from textual.binding import Binding
from textual.screen import ModalScreen

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.model import Model


class ConfirmDeleteDialog(ModalScreen):
    """A confirmation dialog for deleting chats."""

    DEFAULT_CSS = """
    ConfirmDeleteDialog {
        align: center middle;
    }
    
    ConfirmDeleteDialog > Container {
        width: 60;
        height: 12;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }
    
    ConfirmDeleteDialog .dialog-title {
        text-style: bold;
        color: $error;
        text-align: center;
        margin: 0 0 1 0;
    }
    
    ConfirmDeleteDialog .dialog-message {
        text-align: center;
        margin: 0 0 2 0;
        color: $text;
    }
    
    ConfirmDeleteDialog .dialog-buttons {
        height: 3;
        margin: 1 0 0 0;
    }
    
    ConfirmDeleteDialog .dialog-button {
        width: 1fr;
        margin: 0 1;
        text-style: bold;
    }
    
    ConfirmDeleteDialog .delete-button {
        background: $error;
        color: $text;
        
        &:hover {
            background: $error-lighten-1;
        }
    }
    
    ConfirmDeleteDialog .cancel-button {
        background: $surface-lighten-1;
        color: $text;
        
        &:hover {
            background: $surface-lighten-2;
        }
    }
    """

    BINDINGS = [
        Binding("y", "confirm_delete", "Yes", show=False),
        Binding("n", "cancel_delete", "No", show=False),
        Binding("escape", "cancel_delete", "Cancel", show=False),
    ]

    def __init__(self, chat_name: str, **kwargs):
        super().__init__(**kwargs)
        self.chat_name = chat_name

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("⚠️ Delete Chat", classes="dialog-title")
            yield Static(
                f"Are you sure you want to delete '{self.chat_name}'?",
                classes="dialog-message",
            )
            with Horizontal(classes="dialog-buttons"):
                yield Button(
                    "Yes (y)", id="delete-yes", classes="dialog-button delete-button"
                )
                yield Button(
                    "No (n)", id="delete-no", classes="dialog-button cancel-button"
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete-yes":
            self.action_confirm_delete()
        else:
            self.action_cancel_delete()

    def action_confirm_delete(self) -> None:
        self.dismiss(True)

    def action_cancel_delete(self) -> None:
        self.dismiss(False)


class EditNameDialog(ModalScreen):
    """A dialog for editing chat names."""

    DEFAULT_CSS = """
    EditNameDialog {
        align: center middle;
    }
    
    EditNameDialog > Container {
        width: 60;
        height: 12;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }
    
    EditNameDialog .dialog-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin: 0 0 1 0;
    }
    
    EditNameDialog .dialog-input {
        width: 100%;
        margin: 1 0;
        border: solid $primary;
        
        &:focus {
            border: solid $accent;
        }
    }
    
    EditNameDialog .dialog-buttons {
        height: 3;
        margin: 1 0 0 0;
    }
    
    EditNameDialog .dialog-button {
        width: 1fr;
        margin: 0 1;
        text-style: bold;
    }
    
    EditNameDialog .save-button {
        background: $primary;
        color: $text;
        
        &:hover {
            background: $primary-lighten-1;
        }
    }
    
    EditNameDialog .cancel-button {
        background: $surface-lighten-1;
        color: $text;
        
        &:hover {
            background: $surface-lighten-2;
        }
    }
    """

    BINDINGS = [
        Binding("enter", "save_name", "Save", show=False),
        Binding("escape", "cancel_edit", "Cancel", show=False),
    ]

    def __init__(self, current_name: str, **kwargs):
        super().__init__(**kwargs)
        self.current_name = current_name

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("✏️ Edit Chat Name", classes="dialog-title")
            yield Input(
                value=self.current_name,
                placeholder="Enter chat name...",
                classes="dialog-input",
                id="name-input",
            )
            with Horizontal(classes="dialog-buttons"):
                yield Button(
                    "Save (Enter)", id="save-name", classes="dialog-button save-button"
                )
                yield Button(
                    "Cancel (Esc)",
                    id="cancel-edit",
                    classes="dialog-button cancel-button",
                )

    def on_mount(self) -> None:
        self.query_one("#name-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-name":
            self.action_save_name()
        else:
            self.action_cancel_edit()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key pressed in the input field."""
        if event.input.id == "name-input":
            self.action_save_name()

    def action_save_name(self) -> None:
        name_input = self.query_one("#name-input", Input)
        new_name = name_input.value.strip()
        if new_name:
            self.dismiss(new_name)
        else:
            self.dismiss(None)

    def action_cancel_edit(self) -> None:
        self.dismiss(None)


class ModelSelectionDialog(ModalScreen):
    """A dialog for selecting AI models."""

    DEFAULT_CSS = """
    ModelSelectionDialog {
        align: center middle;
    }

    ModelSelectionDialog > Container {
        width: 70;
        height: 20;
        border: thick $primary;
        background: $surface;
        padding: 1;
    }

    ModelSelectionDialog .dialog-title {
        text-style: bold;
        color: $primary;
        text-align: center;
        margin: 0 0 1 0;
    }

    ModelSelectionDialog .current-model {
        text-align: center;
        margin: 0 0 1 0;
        color: $success;
        text-style: italic;
    }

    ModelSelectionDialog .model-list {
        height: 12;
        border: solid $primary;
        background: $surface-lighten-1;
        margin: 0 0 1 0;
    }


    """

    BINDINGS = [
        *[
            Binding(binding, "cancel_selection", "Cancel", show=False)
            for binding in ["escape", "ctrl+c"]
        ],
        *[Binding(binding, "cursor_up", "up", show=False) for binding in ["up", "k"]],
        *[
            Binding(binding, "cursor_down", "down", show=False)
            for binding in ["down", "j"]
        ],
    ]

    def __init__(
        self, models: List["Model"], current_model: Optional[str] = None, **kwargs
    ):
        super().__init__(**kwargs)
        self.models = models
        self.current_model = current_model
        self.selected_model: Optional[str] = None

    def compose(self) -> ComposeResult:
        with Container():
            yield Static("🤖 Select Model", classes="dialog-title")
            if self.current_model:
                yield Static(f"Current: {self.current_model}", classes="current-model")

            # Create list view with models
            model_list = ListView(classes="model-list", id="model-list")
            yield model_list

    def on_mount(self) -> None:
        """Initialize the model list when mounted."""
        model_list = self.query_one("#model-list", ListView)

        # Add models to the list
        for i, model in enumerate(self.models):
            if hasattr(model, "name"):
                model_name = model.name.replace("Chat Model", "")
                if self.current_model and model_name == self.current_model:
                    label = Label(f"✓ {model_name} (current)")
                else:
                    label = Label(model_name)
                list_item = ListItem(label, id=f"model-{i}")
                model_list.append(list_item)

        model_list.focus()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle model selection from list"""
        if event.item and event.item.id and event.item.id.startswith("model-"):
            try:
                index = int(event.item.id.split("-")[1])
                if 0 <= index < len(self.models):
                    selected_model = self.models[index].name
                    self.dismiss(selected_model)
            except (ValueError, IndexError):
                pass

    def action_cancel_selection(self) -> None:
        """Cancel model selection."""
        self.dismiss(None)

    def action_cursor_up(self) -> None:
        """Move cursor up in the list."""
        model_list = self.query_one("#model-list", ListView)
        model_list.action_cursor_up()

    def action_cursor_down(self) -> None:
        """Move cursor down in the list."""
        model_list = self.query_one("#model-list", ListView)
        model_list.action_cursor_down()
