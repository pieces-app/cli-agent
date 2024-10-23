import json
import os
import re

from pieces.settings import Settings

import shutil
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from typing import Any, List, Tuple, Callable,Optional

# Used to create a valid file name when opening to "Opened Snippets"
def sanitize_filename(name):
    """ Sanitize the filename by removing or replacing invalid characters. """
    # Replace spaces with underscores
    name = name.replace(" ", "_")
    # Remove invalid characters
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    return name

def export_code_to_file(code, name, language):
    # Sanitize the name to ensure it's a valid filename
    filename = sanitize_filename(name)
    file_extension = get_file_extension(language)

    # Ensure the directory exists, create it if not
    if not os.path.exists(Settings.open_snippet_dir):
        os.makedirs(Settings.open_snippet_dir)

    # Path to save the extracted code
    file_path = os.path.join(Settings.open_snippet_dir, f'{filename}{file_extension}')

    # Writing the extracted code to a new file
    if isinstance(code, str): # Code string raw
        with open(file_path, 'w') as file:
            file.write(code)
    else: # Image bytes data
        with open(file_path, 'wb') as file:
            file.write(bytes(code))

    return file_path

def get_file_extension(language):
    with open(Settings.extensions_dir) as f:
        extension_mapping = json.load(f)

    # Lowercase the language for case-insensitive matching
    language = language.lower()

    # Return the corresponding file extension or default to '.txt' if not found
    return extension_mapping.get(language, '.txt')

class PiecesSelectMenu:
    def __init__(self, menu_options: List[Tuple], on_enter_callback: Callable, footer_text: Optional[str] = None):
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
            self.menu_window.content = FormattedTextControl(text=self.get_menu_text)
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

        self.menu_window = Window(content=FormattedTextControl(text=self.get_menu_text), always_hide_cursor=True)

        layout_items = [self.menu_window]

        if self.footer_text:
            footer_control = FormattedTextControl(text=self.footer_text)
            footer_window = Window(content=footer_control, height=1, always_hide_cursor=True)
            layout_items.append(footer_window)

        layout = Layout(HSplit(layout_items))

        style = Style.from_dict({
            'selected': 'reverse',
            'unselected': ''
        })

        self.app = Application(layout=layout, key_bindings=bindings, style=style, full_screen=True)
        args = self.app.run()

        if isinstance(args, list):
            self.on_enter_callback(*args)
        elif isinstance(args, str):
            self.on_enter_callback(args)
        elif isinstance(args, dict):
            self.on_enter_callback(**args)
