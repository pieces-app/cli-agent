from pieces.settings import Settings
from pieces.assets import check_assets_existence, AssetsCommandsApi
from typing import List, Tuple, Callable
import subprocess
import shlex
# Import ListCommand from list_commands.py
from list_command import ListCommand, PiecesSelectMenu
# Import necessary functions from assets_command.py
from pieces.assets.assets_command import AssetsCommands

class ExecuteCommand:
    @classmethod
    def execute_command(cls, **kwargs):
        type = kwargs.get("type", "assets")
        max_assets = kwargs.get("max_assets", 10)
        if max_assets < 1:
            print("Max assets must be greater than 0")
            max_assets = 10
        
        if type == "assets":
            cls.execute_assets(max_assets)

    @classmethod
    @check_assets_existence
    def execute_assets(cls, max_assets: int = 10):
        # Use ListCommand to get the assets
        list_command = ListCommand()
        
        # Get the assets
        assets_snapshot = AssetsCommandsApi().assets_snapshot
        assets = []
        for i, uuid in enumerate(list(assets_snapshot.keys())[:max_assets], start=1):
            asset = AssetsCommandsApi.get_asset_snapshot(uuid)
            assets.append((f"{i}: {asset.name}", {"ITEM_INDEX": i, "UUID": uuid}))
