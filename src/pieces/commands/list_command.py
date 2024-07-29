from pieces.settings import Settings
from collections.abc import Iterable
from pieces.assets import check_assets_existence, AssetsCommandsApi
from pieces_os_client.api.applications_api import ApplicationsApi
from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.styles import Style
from typing import List, Tuple, Callable
from pieces.assets.assets_command import AssetsCommands
import time
from .change_model import change_model

class PiecesSelectMenu:
    def __init__(self, menu_options:List[Tuple],on_enter_callback:Callable):
        self.menu_options = menu_options
        self.on_enter_callback = on_enter_callback
        self.current_selection = 0

    def get_menu_text(self):
        result = []
        for i, option in enumerate(self.menu_options):
            if i == self.current_selection:
                result.append(('class:selected', f'> {option[0]}\n'))
            else:
                result.append(('class:unselected', f'  {option[0]}\n'))
        return result

    def run(self):
        bindings = KeyBindings()

        @bindings.add('up')
        def move_up(event):
            if self.current_selection > 0:
                self.current_selection -= 1
            event.app.layout.focus(self.menu_window)

        @bindings.add('down')
        def move_down(event):
            if self.current_selection < len(self.menu_options) - 1:
                self.current_selection += 1
            event.app.layout.focus(self.menu_window)

        @bindings.add('enter')
        def select_option(event):
            args = self.menu_options[self.current_selection][1]
            event.app.exit(result=args)

        menu_control = FormattedTextControl(text=self.get_menu_text)
        self.menu_window = Window(content=menu_control, always_hide_cursor=True)

        layout = Layout(HSplit([self.menu_window]))

        style = Style.from_dict({
            'selected': 'reverse',
            'unselected': ''
        })

        app = Application(layout=layout, key_bindings=bindings, style=style, full_screen=True)
        args = app.run()

        if isinstance(args, list):
            self.on_enter_callback(*args)
        elif isinstance(args, str):
            self.on_enter_callback(args)
        elif isinstance(args, dict):
            self.on_enter_callback(**args)

class ListCommand:
    @classmethod
    def list_command(cls, **kwargs):
        type = kwargs.get("type", "assets")
        max_assets = kwargs.get("max_assets", 10)
        if max_assets < 1:
            print("Max assets must be greater than 0")
            max_assets = 10
        
        if type == "assets":
            cls.list_assets(**kwargs)
        elif type == "apps":
            cls.list_apps()
        elif type == "models":
            cls.list_models()

    @classmethod
    @check_assets_existence
    def list_assets(cls, max_assets: int = 10,**kwargs):
        assets_snapshot = AssetsCommandsApi().assets_snapshot
        assets = []
        for i, uuid in enumerate(list(assets_snapshot.keys())[:max_assets], start=1):
            asset = AssetsCommandsApi.get_asset_snapshot(uuid)
            assets.append((f"{i}: {asset.name}", {"ITEM_INDEX":i,"show_warning":False,**kwargs})) # Pass the args to the open command

        select_menu = PiecesSelectMenu(assets, AssetsCommands.open_asset)
        select_menu.run()

    @classmethod
    def list_models(cls):
        if not hasattr(Settings, 'models'):
            Settings.load_models()
        
        if not Settings.models:
            print("No models available.")
            return

        models = [(f"{idx}: {model_name}", {"MODEL_INDEX":idx,"show_warning":False}) for idx, model_name in enumerate(Settings.models.keys(), start=1)]
        # models.append((f"Currently using: {Settings.model_name} with uuid {Settings.model_id}")) # TODO
        # TODO: add a normal print message
        select_menu = PiecesSelectMenu(models, change_model)
        select_menu.run()

    @classmethod
    def list_apps(cls):
        applications_api = ApplicationsApi(Settings.api_client)
        application_list = applications_api.applications_snapshot()

        if hasattr(application_list, 'iterable') and isinstance(application_list.iterable, Iterable):
            for i, app in enumerate(application_list.iterable, start=1):
                app_name = getattr(app, 'name', 'Unknown').value if hasattr(app, 'name') and hasattr(app.name, 'value') else 'Unknown'
                app_version = getattr(app, 'version', 'Unknown')
                app_platform = getattr(app, 'platform', 'Unknown').value if hasattr(app, 'platform') and hasattr(app.platform, 'value') else 'Unknown'
                print(f"{i}: {app_name}, {app_version}, {app_platform}")
        else:
            print("Error: The 'Applications' object does not contain an iterable list of applications.")
