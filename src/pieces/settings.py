import pickle
import os
from pathlib import Path
import sys
from platformdirs import user_data_dir

from pieces.logger import Logger
from pieces._vendor.pieces_os_client.wrapper import PiecesClient
from pieces._vendor.pieces_os_client.wrapper.version_compatibility import VersionChecker, UpdateEnum
from pieces import __version__
from pieces.gui import (
    print_version_details,
)
from pieces.urls import URLs


class Settings:
    """Settings class for the PiecesCLI"""

    pieces_client = PiecesClient()

    PIECES_OS_MIN_VERSION = "12.0.0"  # Minimum version (12.0.0)
    PIECES_OS_MAX_VERSION = "13.0.0"  # Maximum version (13.0.0)

    TIMEOUT = 40  # Websocket ask timeout

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(__file__)

    # Define the directory path
    # Check if the directory exists, if not, create it
    pieces_data_dir = user_data_dir(
        appauthor="pieces", appname="cli-agent", ensure_exists=True
    )

    logger = Logger(log_dir=pieces_data_dir)  # Will be set on the app startup

    models_file = Path(
        pieces_data_dir,
        "model_data.pkl",
        # model data file just store the model_id that the user is using (eg. {"model_id": UUID })
    )

    _os_id = None
    file_cache = {}

    config_file = Path(pieces_data_dir, "pieces_config.json")

    run_in_loop = False  # is CLI looping?

    # some useful directories
    # extensions_dir
    extensions_dir = os.path.join(BASE_DIR, "commands", "extensions.json")

    mcp_config = os.path.join(pieces_data_dir, "mcp_config.json")

    # open snippet directory
    open_snippet_dir = os.path.join(pieces_data_dir, "opened_snippets")

    _model_name = None

    @classmethod
    def get_model(cls):
        """
        Retrives the model name from the saved file
        """
        if cls._model_name:
            return cls._model_name

        model_id = cls.get_from_pickle(cls.models_file, "model_id")
        if model_id:
            models_reverse = {v: k for k, v in cls.pieces_client.get_models().items()}
            cls._model_name = models_reverse.get(model_id)
        else:
            cls._model_name = cls.pieces_client.model_name

        try:
            cls.pieces_client.model_name = cls._model_name
        except ValueError:
            return cls.pieces_client.model_name
        return cls._model_name

    @classmethod
    def get_auto_commit_model(cls) -> str:
        cls.pieces_client.model_name
        return cls.get_from_pickle(
            cls.models_file, "gemini-2.0-flash-lite-001"
        ) or cls.get_model_by_unique("gemini-2.0-flash-lite-001")

    @classmethod
    def get_model_by_unique(cls, unique, save_to_cache=True) -> str:
        cls.pieces_client.get_models()
        model = [
            model.id
            for model in cls.pieces_client.models_object
            if model.unique == unique
        ][0]
        if save_to_cache:
            cls.file_cache[unique] = model
            cls.dump_pickle(cls.models_file)

        return model

    @classmethod
    def get_model_id(cls):
        """
        Retrives the model id from the saved file
        """
        cls.pieces_client.model_name  # Let's load the models first
        return (
            cls.get_from_pickle(cls.models_file, "model_id")
            or cls.pieces_client.model_id
        )

    @classmethod
    def get_from_pickle(cls, file, key):
        try:
            cache = cls.file_cache.get(str(file))
            if not cache:
                with open(file, "rb") as f:
                    cache = pickle.load(f)
                    cls.file_cache[str(file)] = cache
            return cache.get(key)
        except FileNotFoundError:
            return None

    @classmethod
    def dump_pickle(cls, file):
        """Store data in a pickle file."""
        with open(file, "wb") as f:
            pickle.dump(cls.file_cache, f)

    @classmethod
    def update_model(cls, model_name, model_id):
        cls._model_name = model_name
        cls.file_cache["model_id"] = model_id
        cls.dump_pickle(file=cls.models_file)
        cls.pieces_client.model_name = model_name

    @classmethod
    def startup(cls, bypass_login = False):
        if cls.pieces_client.is_pieces_running():
            cls.version_check()  # Check the version first
            if not bypass_login:
                cls.check_login()
        else:
            if cls.pieces_client.open_pieces_os(): # PiecesOS is running
                return cls.startup(bypass_login)
            else:
                if cls.logger.confirm("Pieces OS is required but wasn’t found or couldn’t be launched.\n"
                    "Do you want to install it now and get started?"):
                    from .command_interface.simple_commands import InstallCommand

                    status_code = InstallCommand.instance.execute()
                    if status_code == 0:
                        return cls.startup(bypass_login)
                    sys.exit(status_code)

            sys.exit(2)  # Exit the program

    @classmethod
    def version_check(cls):
        """Check if the version of PiecesOS is compatible"""
        cls.pieces_os_version = cls.pieces_client.version
        result = VersionChecker(
            cls.PIECES_OS_MIN_VERSION, cls.PIECES_OS_MAX_VERSION, cls.pieces_os_version
        ).version_check()

        # Check compatibility
        if result.update == UpdateEnum.Plugin:
            print(
                "Please update your cli-agent tool. It is not compatible with the current PiecesOS version"
            )
            print(
                URLs.DOCS_CLI.value
            )  # TODO: We might need to add a link a better link here
            print_version_details(cls.pieces_os_version, __version__)
            sys.exit(2)
        elif result.update == UpdateEnum.PiecesOS:
            # TODO: Use the update POS endpoint
            print(
                "Please update PiecesOS. It is not compatible with the current cli-agent version"
            )
            print(URLs.DOCS_INSTALLATION.value)
            print_version_details(cls.pieces_os_version, __version__)
            sys.exit(2)

    @classmethod
    def check_login(cls):
        user = cls.pieces_client.user_api.user_snapshot().user
        if not user:
            if cls.logger.confirm("Please sign into Pieces to use this feature. Do you want to sign in now?"):
                cls.pieces_client.user.login(True)
                user = cls.pieces_client.user_api.user_snapshot().user
        if user:
            return
        sys.exit(1)

    @classmethod
    def show_error(cls, error, error_message=None):
        cls.logger.console_error.print(f"[red]{error}")
        cls.logger.console_error.print(f"[red]{error_message}") if error_message else None
        if not cls.run_in_loop:
            sys.exit(2)

    @classmethod
    def get_os_id(cls):
        from pieces._vendor.pieces_os_client.models.application_name_enum import ApplicationNameEnum

        if cls._os_id:
            return cls._os_id
        for app in cls.pieces_client.applications_api.applications_snapshot().iterable:
            if app.name == ApplicationNameEnum.OS_SERVER:
                cls._os_id = app.id
                return app.id
