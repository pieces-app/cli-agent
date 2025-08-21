"""Base list panel widget with common functionality for item management."""

from abc import abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from textual.app import ComposeResult
from textual.widgets import Static, Button
from textual.containers import ScrollableContainer, Container
from textual.reactive import reactive
from textual.widget import Widget
from textual.binding import Binding
from textual.message import Message
from textual.css.query import NoMatches

from .base_item import BaseItem
from pieces.settings import Settings


class BaseListPanel(ScrollableContainer):
    """Base class for list panels with common functionality."""

    DEFAULT_CSS = """
    BaseListPanel {
        border: solid $secondary;
        border-title-color: $secondary;
        border-title-style: bold;
        scrollbar-background: $surface;
        scrollbar-color: $secondary;
        scrollbar-color-hover: $accent;
        
        &:focus {
            border: solid $accent;
            border-title-color: $accent;
            border-title-style: bold;
        }
    }
    
    BaseListPanel .new-item-button {
        width: 100%;
        height: 3;
        margin: 0 0 1 0;
        background: $primary;
        color: $text;
        border: none;
        text-style: bold;
        
        &:hover {
            background: $primary-lighten-1;
        }
        
        &:focus {
            background: $primary-lighten-2;
        }
    }
    
    BaseListPanel .items-list {
        width: 100%;
        height: 1fr;
        overflow-y: auto;
    }
    
    BaseListPanel .empty-items {
        width: 100%;
        text-align: center;
        padding: 2;
        color: $text-muted;
        text-style: italic;
        height: auto;
    }
    """

    items: reactive[List[tuple]] = reactive([])  # (item, title, subtitle)
    active_item: reactive[Optional[Any]] = reactive(None)

    BINDINGS = [
        *[
            Binding(key, "select_next", "Next item", show=False)
            for key in ["j", "down"]
        ],
        *[
            Binding(key, "select_previous", "Previous item", show=False)
            for key in ["k", "up"]
        ],
        Binding("enter", "open_selected", "Open item", show=False),
        Binding("r", "rename_item", "Rename item", show=False),
        Binding("d", "delete_item", "Delete item", show=False),
    ]

    def __init__(
        self,
        panel_title: str,
        empty_message: str,
        show_new_button: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.border_title = panel_title
        self._empty_message = empty_message
        self._show_new_button = show_new_button

        # Efficient tracking: item_id -> BaseItem widget
        self._item_widgets: Dict[str, BaseItem] = {}
        # Track current item order for positioning
        self._item_order: List[str] = []
        self._selected_item_id: Optional[str] = None

    def compose(self) -> ComposeResult:
        """Compose the list panel."""
        # New Item button at the top (optional)
        if self._show_new_button:
            new_item_btn = Button(
                self.get_new_button_text(), classes="new-item-button", id="new-item-btn"
            )
            new_item_btn.can_focus = False
            yield new_item_btn

        # Items list container
        with Container(classes="items-list", id="items-container"):
            yield Static(self._empty_message, classes="empty-items", id="empty-state")

    @abstractmethod
    def get_new_button_text(self) -> str:
        """Get the text for the new item button."""
        pass

    @abstractmethod
    def get_item_id(self, item: Any) -> str:
        """Get a unique ID for an item."""
        pass

    @abstractmethod
    def create_item_widget(self, item: Any, title: str, subtitle: str) -> BaseItem:
        """Create a widget for an item."""
        pass

    @abstractmethod
    def create_new_item_message(self) -> Message:
        """Create message for new item request."""
        pass

    def load_items(self, items):
        """Load items with efficient incremental updates."""
        if items and not isinstance(items[0], tuple):
            converted_items = []
            for item in items:
                title, subtitle = self.extract_item_display_info(item)
                converted_items.append((item, title, subtitle))
            self.items = converted_items
        else:
            # Already in tuple format
            self.items = items

        self._update_items_incrementally()

        # Select first item if available and none selected
        if self.items and self._selected_item_id is None and self._item_order:
            self._selected_item_id = self._item_order[0]
            self._update_visual_selection()

    @abstractmethod
    def extract_item_display_info(self, item: Any) -> Tuple[str, str]:
        """Extract title and subtitle from an item."""
        pass

    def _update_items_incrementally(self):
        """Efficiently update items - only add/remove/update what changed."""
        try:
            items_container = self.query_one("#items-container")
        except NoMatches:
            return

        # Get current item IDs from the new data
        new_item_ids = {self.get_item_id(item) for item, _, _ in self.items}
        current_item_ids = set(self._item_widgets.keys())

        # Calculate what changed
        items_to_add = new_item_ids - current_item_ids
        items_to_remove = current_item_ids - new_item_ids
        items_to_update = new_item_ids & current_item_ids

        # Remove deleted items
        for item_id in items_to_remove:
            if item_id in self._item_widgets:
                widget = self._item_widgets[item_id]
                if widget.is_mounted:
                    widget.remove()
                del self._item_widgets[item_id]
                if item_id in self._item_order:
                    self._item_order.remove(item_id)

        # Hide/show empty state based on whether we have items
        empty_state = items_container.query_one("#empty-state")
        if self.items:
            empty_state.display = False
        else:
            empty_state.display = True
            # Clear everything when no items
            self._item_widgets.clear()
            self._item_order.clear()
            return

        # Create mapping for efficient lookup
        item_data_by_id = {
            self.get_item_id(item): (item, title, subtitle)
            for item, title, subtitle in self.items
        }

        # Add new items
        for item_id in items_to_add:
            if item_id in item_data_by_id:
                item, title, subtitle = item_data_by_id[item_id]
                self._add_item_widget(item, title, subtitle, items_container)

        # Update existing items (title, subtitle, active state)
        for item_id in items_to_update:
            if item_id in item_data_by_id and item_id in self._item_widgets:
                item, title, subtitle = item_data_by_id[item_id]
                self._update_item_widget(item_id, item, title, subtitle)

        # Reorder widgets to match the new item order
        self._reorder_item_widgets(items_container)

    def _add_item_widget(self, item: Any, title: str, subtitle: str, container: Widget):
        """Add a new item widget efficiently."""
        is_active = self._is_item_active(item)

        item_widget = self.create_item_widget(item, title, subtitle)
        item_widget.set_active(is_active)

        # Use item ID for unique identification
        item_id = self.get_item_id(item)
        item_widget.id = f"item-{item_id}"
        self._item_widgets[item_id] = item_widget
        self._item_order.append(item_id)

        container.mount(item_widget)

    def _is_item_active(self, item: Any) -> bool:
        """Check if an item is currently active."""
        return item == self.active_item

    def _update_item_widget(self, item_id: str, item: Any, title: str, subtitle: str):
        """Update an existing item widget efficiently."""
        if item_id not in self._item_widgets:
            return

        widget = self._item_widgets[item_id]

        # Update widget data if changed
        if widget.title != title:
            widget.title = title
            # Update the title widget in the UI
            title_widget = widget.query_one(".item-title", Static)
            title_widget.update(title)

        if widget.subtitle != subtitle:
            widget.subtitle = subtitle
            # Update subtitle widget if it exists
            subtitle_widgets = widget.query(".item-subtitle")
            if subtitle_widgets and subtitle:
                subtitle_widget = subtitle_widgets[0]
                if hasattr(subtitle_widget, "update"):
                    subtitle_widget.update(subtitle)  # type: ignore

        # Update active state
        is_active = self._is_item_active(item)
        widget.set_active(is_active)

    def _reorder_item_widgets(self, container: Widget):
        """Reorder widgets to match the new item order efficiently."""
        # Build new order based on current items list
        new_order = []
        for item, _, _ in self.items:
            item_id = self.get_item_id(item)
            if item_id in self._item_widgets:
                new_order.append(item_id)

        # Only reorder if the order actually changed
        if new_order != self._item_order:
            self._item_order = new_order

            # Move widgets to correct positions
            for i, item_id in enumerate(self._item_order):
                if item_id in self._item_widgets:
                    widget = self._item_widgets[item_id]
                    try:
                        # Move widget to the correct position
                        if i == 0:
                            # Move to beginning
                            children = list(container.children)
                            if children:
                                container.move_child(widget, before=children[0])
                        else:
                            # Move after the previous widget
                            prev_item_id = self._item_order[i - 1]
                            if prev_item_id in self._item_widgets:
                                prev_widget = self._item_widgets[prev_item_id]
                                container.move_child(widget, after=prev_widget)
                    except (ValueError, RuntimeError):
                        pass

    def set_active_item(self, item: Optional[Any]):
        """Set the active item - only update affected widgets."""
        if self.active_item != item:
            old_active_id = (
                self.get_item_id(self.active_item) if self.active_item else None
            )
            new_active_id = self.get_item_id(item) if item else None

            self.active_item = item

            # Update only the affected widgets
            if old_active_id and old_active_id in self._item_widgets:
                old_widget = self._item_widgets[old_active_id]
                old_widget.set_active(False)

            if new_active_id and new_active_id in self._item_widgets:
                new_widget = self._item_widgets[new_active_id]
                new_widget.set_active(True)

    def _update_visual_selection(self):
        """Update visual selection efficiently using widget dictionary."""
        # Clear all selections first
        for widget in self._item_widgets.values():
            widget.deselect()

        if self._selected_item_id and self._selected_item_id in self._item_widgets:
            selected_widget = self._item_widgets[self._selected_item_id]
            selected_widget.select()

            # Scroll to selected widget
            try:
                self.scroll_to_widget(selected_widget, animate=True)
            except (ValueError, RuntimeError):
                # Widget may not be scrollable or visible
                pass

    # Keyboard navigation
    def action_select_next(self):
        """Select the next item."""
        if not self._item_order:
            return

        if self._selected_item_id is None:
            self._selected_item_id = self._item_order[0]
        else:
            try:
                current_index = self._item_order.index(self._selected_item_id)
                next_index = min(current_index + 1, len(self._item_order) - 1)
                self._selected_item_id = self._item_order[next_index]
            except ValueError:
                self._selected_item_id = self._item_order[0]

        self._update_visual_selection()

    def action_select_previous(self):
        """Select the previous item."""
        if not self._item_order:
            return

        if self._selected_item_id is None:
            self._selected_item_id = self._item_order[-1]
        else:
            try:
                current_index = self._item_order.index(self._selected_item_id)
                prev_index = max(current_index - 1, 0)
                self._selected_item_id = self._item_order[prev_index]
            except ValueError:
                self._selected_item_id = self._item_order[-1]

        self._update_visual_selection()

    def action_open_selected(self):
        """Open the selected item."""
        if self._selected_item_id and self._selected_item_id in self._item_widgets:
            item_widget = self._item_widgets[self._selected_item_id]
            item_widget.on_click()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new-item-btn" and self._show_new_button:
            self.post_message(self.create_new_item_message())
            event.stop()

    def on_click(self, event) -> None:
        """Handle click events on child items."""

        # Check if the click was on one of our item widgets or their children
        clicked_widget = event.widget
        Settings.logger.info(
            f"BaseListPanel: Click detected on widget {clicked_widget}"
        )

        # Find the BaseItem by traversing up the widget tree
        target_item = None
        current_widget = clicked_widget

        # Traverse up the widget tree to find a BaseItem
        while current_widget is not None:
            if isinstance(current_widget, BaseItem):
                target_item = current_widget
                break
            current_widget = current_widget.parent

        if target_item:
            Settings.logger.info(f"BaseListPanel: Found BaseItem: {target_item}")
            # Find the item ID for this widget and update selection
            for item_id, widget in self._item_widgets.items():
                if widget == target_item:
                    Settings.logger.info(
                        f"BaseListPanel: Updating selection to item {item_id}"
                    )
                    self._selected_item_id = item_id
                    self._update_visual_selection()
                    break
        else:
            Settings.logger.info(f"BaseListPanel: No BaseItem found in widget tree")

    def clear_items(self):
        """Clear all items efficiently."""
        # Remove all widgets
        for widget in self._item_widgets.values():
            if widget.is_mounted:
                try:
                    widget.remove()
                except (RuntimeError, ValueError):
                    pass  # Widget may already be removed

        # Clear tracking
        self._item_widgets.clear()
        self._item_order.clear()

        # Clear data
        self.items.clear()
        self.active_item = None
        self._selected_item_id = None

        # Show empty state - but only if the container exists
        try:
            items_container = self.query_one("#items-container")
            empty_state = items_container.query_one("#empty-state")
            empty_state.display = True
        except NoMatches:
            pass
