from collections.abc import Iterable
import threading

from pieces.settings import Settings
from pieces._vendor.pieces_os_client.wrapper.basic_identifier.asset import BasicAsset
from .change_model import change_model
from .assets_command import check_assets_existence, AssetsCommands


class ListCommand:
    @classmethod
    def list_command(cls, **kwargs):
        type = kwargs.get("type", "materials")

        if type == "materials":
            cls.list_assets(**kwargs)
        elif type == "apps":
            cls.list_apps()
        elif type == "models":
            cls.list_models()

    @classmethod
    @check_assets_existence
    def list_assets(cls, **kwargs):
        from pieces.utils import PiecesSelectMenu

        assets = kwargs.get(
            "assets",
            [BasicAsset(item.id) for item in BasicAsset.get_identifiers()],  # type: ignore[assignment]
        )

        select_menu = PiecesSelectMenu(
            [],
            AssetsCommands.open_asset,
            kwargs.get("footer"),
            title="Select a material",
        )

        def update_assets():
            for i, asset in enumerate(assets, start=1):
                try:
                    select_menu.add_entry(
                        (f"{i}: {asset.name}", {"asset_id": asset.id, **kwargs})
                    )
                except AttributeError:
                    pass

        threading.Thread(target=update_assets).start()
        select_menu.run()

    @classmethod
    def list_models(cls):
        from pieces.utils import PiecesSelectMenu

        models = [
            (f"{idx}: {model_name}", {"MODEL_INDEX": idx})
            for idx, model_name in enumerate(
                Settings.pieces_client.available_models_names, start=1
            )
        ]
        model_info = Settings.model_config.model
        select_menu = PiecesSelectMenu(
            models,
            change_model,
            f"Currently using: {model_info.name}" if model_info else None,
            title="Select a LLM",
        )
        select_menu.run()

    @classmethod
    def list_apps(cls):
        application_list = (
            Settings.pieces_client.applications_api.applications_snapshot()
        )

        if hasattr(application_list, "iterable") and isinstance(
            application_list.iterable, Iterable
        ):
            for i, app in enumerate(application_list.iterable, start=1):
                app_name = (
                    getattr(app, "name", "Unknown").value  # type: ignore[assignment]
                    if hasattr(app, "name") and hasattr(app.name, "value")
                    else "Unknown"
                )
                app_version = getattr(app, "version", "Unknown")
                app_platform = (
                    getattr(app, "platform", "Unknown").value  # type: ignore[assignment]
                    if hasattr(app, "platform") and hasattr(app.platform, "value")
                    else "Unknown"
                )
                Settings.logger.print(f"{i}: {app_name}, {app_version}, {app_platform}")
        else:
            Settings.logger.print(
                "Error: The 'Applications' object does not contain an iterable list of applications."
            )
