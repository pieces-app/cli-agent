from pieces.settings import Settings
from .assets_command import check_assets_existence, AssetsCommands
import subprocess
from pieces.utils import PiecesSelectMenu
from pieces._vendor.pieces_os_client.models.classification_specific_enum import ClassificationSpecificEnum


class ExecuteCommand:
    @classmethod
    @check_assets_existence
    def execute_command(cls, **kwargs):

        assets = [
            (f"{asset.name}", {"asset_id": asset.id,  "asset": asset})
            for i, asset in enumerate(list(Settings.pieces_client.assets()),
                                      start=1)
            if asset.classification in (ClassificationSpecificEnum.SH,
                                        ClassificationSpecificEnum.BAT)
        ]

        if not assets:
            Settings.logger.print("No shell or bash assets found")
            return

        def open_and_execute_asset(**kwargs):
            AssetsCommands.open_asset(**kwargs)
            cls.execute_asset(**kwargs)

        select_menu = PiecesSelectMenu(assets, open_and_execute_asset, title="Select a material to execute")
        select_menu.run()

    @classmethod
    def execute_asset(cls, **kwargs):
        asset = kwargs["asset"]

        try:
            if asset.classification == ClassificationSpecificEnum.BASH:
                result = subprocess.run(
                    ['bash', '-c', asset.raw_content], capture_output=True,
                    text=True)
            elif asset.classification == ClassificationSpecificEnum.SH:
                result = subprocess.run(
                    asset.raw_content, shell=True, capture_output=True,
                    text=True)
            else:
                raise ValueError(
                    f"Unsupported classification {asset.classification}")
            Settings.logger.print(f"Executing {asset.classification.value} command:")
            Settings.logger.print(result.stdout)
            if result.stderr:
                Settings.logger.print("Errors:")
                Settings.logger.print(result.stderr)
        except subprocess.CalledProcessError as e:
            Settings.logger.print(f"Error executing command: {e}")
        except Exception as e:
            Settings.logger.print(f"An error occurred: {e}")
