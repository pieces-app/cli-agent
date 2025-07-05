import shutil
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.widgets import Box
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from typing import Any, List, Tuple, Callable, Optional
from .core.extensions import extensions_dict


def get_file_extension(language):
    # Lowercase the language for case-insensitive matching
    language = language.lower()

    # Return the corresponding file extension or default to '.txt' if not found
    return extensions_dict.get(language, ".txt")


class PiecesSelectMenu:
    def __init__(
        self,
        menu_options: List[Tuple],
        on_enter_callback: Callable,
        footer_text: Optional[str] = None,
        title: Optional[str] = "Select an option",
    ):
        self.menu_options = list(menu_options)  # Ensure it's a list
        self.on_enter_callback = on_enter_callback
        self.current_selection = 0
        self.footer_text = footer_text
        self.title = title
        self.update_visible_range()

    def update_visible_range(self):
        terminal_size = shutil.get_terminal_size()
        # Reserve space for title, borders and footer
        max_visible_items = terminal_size.lines - 4
        self.visible_start = max(0, self.current_selection - max_visible_items // 2)
        self.visible_end = min(
            len(self.menu_options), self.visible_start + max_visible_items
        )

    def add_entry(self, entry: Tuple[str, Any]):
        """Add a new entry to the menu and update the layout."""
        self.menu_options.append(entry)
        self.update_visible_range()
        self.update_app()

    def get_menu_text(self):
        result = []

        for i, option in enumerate(
            self.menu_options[self.visible_start : self.visible_end]
        ):
            idx = i + self.visible_start

            if idx == self.current_selection:
                # Selected item gets highlighted
                result.append(("class:selected", f"|▶ {option[0]}\n"))
            else:
                result.append(("class:unselected", f"| {option[0]}\n"))

        return result

    def get_title_text(self):
        return [("class:title", f" {self.title} ")]

    def get_footer_text(self):
        if self.footer_text:
            return [("class:footer", f" {self.footer_text} ")]
        else:
            return [
                ("class:footer", " ↑/↓: Navigate • Enter: Select • q/Ctrl+C: Quit ")
            ]

    def update_app(self):
        if hasattr(self, "app"):
            self.menu_window.content = FormattedTextControl(text=self.get_menu_text)
            self.app.invalidate()
        else:
            pass

    def run(self):
        bindings = KeyBindings()

        @bindings.add("up")
        def move_up(event):
            if self.current_selection > 0:
                self.current_selection -= 1
                self.update_visible_range()
            event.app.layout.focus(self.menu_window)

        @bindings.add("down")
        def move_down(event):
            if self.current_selection < len(self.menu_options) - 1:
                self.current_selection += 1
                self.update_visible_range()
            event.app.layout.focus(self.menu_window)

        @bindings.add("pageup")
        def page_up(event):
            items_per_page = self.visible_end - self.visible_start
            self.current_selection = max(0, self.current_selection - items_per_page)
            self.update_visible_range()
            event.app.layout.focus(self.menu_window)

        @bindings.add("pagedown")
        def page_down(event):
            items_per_page = self.visible_end - self.visible_start
            self.current_selection = min(
                len(self.menu_options) - 1, self.current_selection + items_per_page
            )
            self.update_visible_range()
            event.app.layout.focus(self.menu_window)

        @bindings.add("home")
        def go_to_top(event):
            self.current_selection = 0
            self.update_visible_range()
            event.app.layout.focus(self.menu_window)

        @bindings.add("end")
        def go_to_bottom(event):
            self.current_selection = len(self.menu_options) - 1
            self.update_visible_range()
            event.app.layout.focus(self.menu_window)

        @bindings.add("enter")
        def select_option(event):
            args = self.menu_options[self.current_selection][1]
            event.app.exit(result=args)

        @bindings.add("c-c")
        @bindings.add("q")
        def exit_app(event):
            event.app.exit(result=False)

        self.menu_window = Window(
            content=FormattedTextControl(text=self.get_menu_text),
            always_hide_cursor=True,
            wrap_lines=False,
        )

        title_window = Window(
            content=FormattedTextControl(text=self.get_title_text),
            height=1,
            always_hide_cursor=True,
        )

        footer_window = Window(
            content=FormattedTextControl(text=self.get_footer_text),
            height=1,
            always_hide_cursor=True,
        )

        # Create a framed layout with title and menu
        menu_container = Box(
            body=HSplit([title_window, self.menu_window, footer_window]),
            padding=1,
            padding_left=2,
            padding_right=2,
            style="class:menu-box",
        )

        layout = Layout(menu_container)

        style = Style.from_dict(
            {
                "selected": "reverse bold",
                "title": "ansicyan bold",
                "footer": "ansibrightblack italic",
            }
        )

        self.app = Application(
            layout=layout,
            key_bindings=bindings,
            style=style,
            full_screen=True,
            mouse_support=True,
        )

        args = self.app.run()
        if args is False:
            return None

        if isinstance(args, list):
            return self.on_enter_callback(*args)
        elif isinstance(args, str):
            return self.on_enter_callback(args)
        elif isinstance(args, dict):
            return self.on_enter_callback(**args)
