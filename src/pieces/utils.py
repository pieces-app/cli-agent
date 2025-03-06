import shutil
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from typing import Any, List, Tuple, Callable, Optional
from .commands.extensions import extensions_dict


def get_file_extension(language):
    # Lowercase the language for case-insensitive matching
    language = language.lower()

    # Return the corresponding file extension or default to '.txt' if not found
    return extensions_dict.get(language, '.txt')


class PiecesSelectMenu:
    def __init__(self, menu_options: List[Tuple],
                 on_enter_callback: Callable,
                 footer_text: Optional[str] = None):
        self.menu_options = list(menu_options)  # Ensure it's a list
        self.on_enter_callback = on_enter_callback
        self.current_selection = 0
        self.footer_text = footer_text
        self.update_visible_range()

    def update_visible_range(self):
        terminal_size = shutil.get_terminal_size()
        self.visible_start = 0
        self.visible_end = terminal_size.lines - 2

    def add_entry(self, entry: Tuple[str, Any]):
        """Add a new entry to the menu and update the layout."""
        self.menu_options.append(entry)
        self.update_visible_range()
        self.update_app()

    def get_menu_text(self):
        result = []
        for i, option in enumerate(self.menu_options[self.visible_start:self.visible_end]):
            if i + self.visible_start == self.current_selection:
                result.append(('class:selected', f'> {option[0]}\n'))
            else:
                result.append(('class:unselected', f'  {option[0]}\n'))
        return result

    def update_app(self):
        if hasattr(self, "app"):
            self.menu_window.content = FormattedTextControl(
                text=self.get_menu_text)
            self.app.invalidate()
            # self.app.layout.focus(self.menu_window)
        else:
            pass
            # raise ValueError("App not initialized")

    def run(self):
        bindings = KeyBindings()

        @bindings.add('up')
        def move_up(event):
            if self.current_selection > 0:
                self.current_selection -= 1
                if self.current_selection < self.visible_start:
                    self.visible_start -= 1
                    self.visible_end -= 1
            event.app.layout.focus(self.menu_window)

        @bindings.add('down')
        def move_down(event):
            if self.current_selection < len(self.menu_options) - 1:
                self.current_selection += 1
                if self.current_selection >= self.visible_end:
                    self.visible_start += 1
                    self.visible_end += 1
            event.app.layout.focus(self.menu_window)

        @bindings.add('enter')
        def select_option(event):
            args = self.menu_options[self.current_selection][1]
            event.app.exit(result=args)

        @bindings.add('c-c')
        @bindings.add('q')
        def exit_app(event):
            event.app.exit()

        self.menu_window = Window(content=FormattedTextControl(
            text=self.get_menu_text), always_hide_cursor=True)

        layout_items = [self.menu_window]

        if self.footer_text:
            footer_control = FormattedTextControl(text=self.footer_text)
            footer_window = Window(
                content=footer_control, height=1, always_hide_cursor=True)
            layout_items.append(footer_window)

        layout = Layout(HSplit(layout_items))

        style = Style.from_dict({
            'selected': 'reverse',
            'unselected': ''
        })

        self.app = Application(
            layout=layout,
            key_bindings=bindings,
            style=style,
            full_screen=True)
        args = self.app.run()

        if isinstance(args, list):
            self.on_enter_callback(*args)
        elif isinstance(args, str):
            self.on_enter_callback(args)
        elif isinstance(args, dict):
            self.on_enter_callback(**args)
