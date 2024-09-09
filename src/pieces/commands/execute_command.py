from ..assets import check_assets_existence, AssetsCommandsApi
import subprocess
from .list_command import PiecesSelectMenu
from ..assets.assets_command import AssetsCommands


class ExecuteCommand:
    @classmethod
    @check_assets_existence
    def execute_command(cls, max_assets: int = 10,**kwargs):
        if max_assets < 1:
            print("Max assets must be greater than 0")
            max_assets = 10
        assets_snapshot = AssetsCommandsApi().assets_snapshot
        assets = []
        
        for i, uuid in enumerate(list(assets_snapshot.keys())[:max_assets], start=1):
            asset = AssetsCommandsApi.get_asset_snapshot(uuid)
            classification = cls.get_asset_classification(asset)
            if classification in ["bat","sh"]:
                assets.append((f"{i}: {asset.name}", {"ITEM_INDEX": i, "UUID": uuid, "CLASSIFICATION": classification,"show_warning":False}))
        
        if not assets:
            print("No shell or bash assets found")
            return
        
        def open_and_execute_asset(**kwargs):
            AssetsCommands.open_asset(**kwargs)
            cls.execute_asset(**kwargs)
        
        select_menu = PiecesSelectMenu(assets, open_and_execute_asset)
        select_menu.run()

    @staticmethod
    def get_asset_classification(asset):
        try:
            return asset.original.reference.classification.specific.value
        except AttributeError:
            return "unknown"

    @classmethod
    def execute_asset(cls, **kwargs):
        uuid = kwargs.get("UUID")
        classification = kwargs.get("CLASSIFICATION")
        asset = AssetsCommandsApi.get_asset_snapshot(uuid)
        asset_dict = AssetsCommandsApi.extract_asset_info(asset)
        
        cls.execute_command_in_subprocess(asset_dict["raw"], classification)

    @staticmethod
    def execute_command_in_subprocess(command: str, classification: str):
        try:
            if classification == "bat":
                result = subprocess.run(['bash', '-c', command], capture_output=True, text=True)
            elif classification == "sh":
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
            else:
                print(f"Unsupported asset classification: {classification}")
                return
            
            print(f"Executing {classification} command:")
            print(result.stdout)
            if result.stderr:
                print("Errors:")
                print(result.stderr)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

