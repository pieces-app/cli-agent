from collections.abc import Iterable

from pieces.settings import Settings
from pieces.utils import PiecesSelectMenu

from .change_model import change_model
from .assets_command import check_assets_existence, AssetsCommands


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
        assets = kwargs.get("assets",Settings.pieces_client.assets()[:max_assets])

        select_menu = PiecesSelectMenu(
            [
                (f"{i}: {asset.name}", {"ITEM_INDEX":i,"show_warning":False,**kwargs})
                for i, asset in enumerate(assets,start=1)
            ],
             AssetsCommands.open_asset,kwargs.get("footer"))
        select_menu.run()

    @classmethod
    def list_models(cls):

        models = [(f"{idx}: {model_name}", {"MODEL_INDEX":idx,"show_warning":False}) 
        for idx, model_name in enumerate(Settings.pieces_client.available_models_names, start=1)]
        select_menu = PiecesSelectMenu(models, change_model,f"Currently using: {Settings.get_model()}")
        select_menu.run()

    @classmethod
    def list_apps(cls):
        application_list = Settings.pieces_client.applications_api.applications_snapshot()

        if hasattr(application_list, 'iterable') and isinstance(application_list.iterable, Iterable):
            for i, app in enumerate(application_list.iterable, start=1):
                app_name = getattr(app, 'name', 'Unknown').value if hasattr(app, 'name') and hasattr(app.name, 'value') else 'Unknown'
                app_version = getattr(app, 'version', 'Unknown')
                app_platform = getattr(app, 'platform', 'Unknown').value if hasattr(app, 'platform') and hasattr(app.platform, 'value') else 'Unknown'
                print(f"{i}: {app_name}, {app_version}, {app_platform}")
        else:
            print("Error: The 'Applications' object does not contain an iterable list of applications.")
