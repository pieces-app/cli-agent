from pieces.settings import Settings
from collections.abc import Iterable
from pieces.assets import check_assets_existence,AssetsCommandsApi

from pieces_os_client.api.applications_api import ApplicationsApi


class ListCommand:
    @classmethod
    def list_command(cls,**kwargs):
        type = kwargs.get("type","assets")
        max_assets = kwargs.get("max_assets",10)
        if max_assets < 1:
            print("Max assets must be greater than 0")
            max_assets = 10
        
        if type == "assets":
            cls.list_assets(max_assets)
        elif type == "apps":
           cls.list_apps()
        elif type == "models":
            cls.list_models()
    @staticmethod
    def list_models():
        for idx,model_name in enumerate(Settings.models,start=1):
            print(f"{idx}: {model_name}")
        print(f"Currently using: {Settings.model_name} with uuid {Settings.model_id}")

    @staticmethod
    def list_apps():
        # Get the list of applications
        
        applications_api = ApplicationsApi(Settings.api_client)

        application_list = applications_api.applications_snapshot()
        # Check if the application_list object has an iterable attribute and if it is an instance of Iterable
        if hasattr(application_list, 'iterable') and isinstance(application_list.iterable, Iterable):
            # Iterate over the applications in the list
            for i, app in enumerate(application_list.iterable, start=1):
                # Get the name of the application, default to 'Unknown' if not available
                app_name = getattr(app, 'name', 'Unknown').value if hasattr(app, 'name') and hasattr(app.name, 'value') else 'Unknown'
                # Get the version of the application, default to 'Unknown' if not available
                app_version = getattr(app, 'version', 'Unknown')
                # Get the platform of the application, default to 'Unknown' if not available
                app_platform = getattr(app, 'platform', 'Unknown').value if hasattr(app, 'platform') and hasattr(app.platform, 'value') else 'Unknown'
                    
                # Print the application details
                print(f"{i}: {app_name}, {app_version}, {app_platform}")
        else:
            # Print an error message if the 'Applications' object does not contain an iterable list of applications
            print("Error: The 'Applications' object does not contain an iterable list of applications.")
    
    @staticmethod
    @check_assets_existence
    def list_assets(max_assets:int=10):
        assets_snapshot = AssetsCommandsApi().assets_snapshot
        for i, uuid in enumerate(list(assets_snapshot.keys())[:max_assets], start=1):
            asset = assets_snapshot[uuid]
            if not asset:
                asset = AssetsCommandsApi.get_asset_snapshot(uuid)
            print(f"{i}: {asset.name}")