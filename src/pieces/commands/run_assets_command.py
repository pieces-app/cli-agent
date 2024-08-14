from pieces.settings import Settings
from pieces.assets import check_assets_existence, AssetsCommandsApi
from typing import List, Tuple, Callable
import subprocess
from enum import Enum
from list_command import PiecesSelectMenu
from pieces.assets.assets_command import AssetsCommands

class AssetClassification(Enum):
    SHELL = "sh"

class ExecuteCommand:
    @classmethod
    @check_assets_existence
    def execute_command(cls, max_assets: int = 10):
        if max_assets < 1:
            print("Max assets must be greater than 0")
            max_assets = 10

        assets_snapshot = AssetsCommandsApi().assets_snapshot
        shell_assets = []
        
        for i, uuid in enumerate(list(assets_snapshot.keys()), start=1):
            asset = AssetsCommandsApi.get_asset_snapshot(uuid)
            classification = cls.get_asset_classification(asset)
            if classification == AssetClassification.SHELL.value:
                shell_assets.append((f"{len(shell_assets) + 1}: {asset.name}", {"ITEM_INDEX": i, "UUID": uuid, "CLASSIFICATION": classification}))
            
            if len(shell_assets) == max_assets:
                break

        if not shell_assets:
            print("No shell assets found")
            return
