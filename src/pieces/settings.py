import pickle
import os
from pathlib import Path
import sys
from platformdirs import user_data_dir
from .wrapper import PiecesClient
from .wrapper.version_compatibility import VersionChecker, UpdateEnum
from pieces import __version__
from pieces.gui import server_startup_failed, print_pieces_os_link, print_version_details

import webbrowser
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse


class Settings:
    """Settings class for the PiecesCLI"""
    pieces_client = PiecesClient()

    PIECES_OS_MIN_VERSION = "11.0.0"  # Minium version (11.0.0)
    PIECES_OS_MAX_VERSION = "12.0.0"  # Maxium version (12.0.0)

    TIMEOUT = 20  # Websocket ask timeout

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(__file__)

    # Define the directory path
    # Check if the directory exists, if not, create it
    pieces_data_dir = user_data_dir(
        appauthor="pieces", appname="cli-agent", ensure_exists=True)

    models_file = Path(
        pieces_data_dir, "model_data.pkl"
        # model data file just store the model_id that the user is using (eg. {"model_id": UUID })
    )

    file_cache = {}

    config_file = Path(pieces_data_dir, "pieces_config.json")

    run_in_loop = False  # is CLI looping?

    # some useful directories
    # extensions_dir
    extensions_dir = os.path.join(BASE_DIR, 'commands', 'extensions.json')

    # open snippet directory
    open_snippet_dir = os.path.join(os.getcwd(), 'opened_snippets')

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
            models_reverse = {v: k for k,
                              v in cls.pieces_client.get_models().items()}
            cls._model_name = models_reverse.get(model_id)
        else:
            cls._model_name = cls.pieces_client.model_name

        try:
            cls.pieces_client.model_name = cls._model_name
        except ValueError:
            return cls.pieces_client.model_name
        return cls._model_name

    @classmethod
    def get_model_id(cls):
        """
                Retrives the model id from the saved file
        """
        cls.pieces_client.model_name  # Let's load the models first
        return cls.get_from_pickle(cls.models_file, "model_id") or cls.pieces_client.model_id

    @classmethod
    def get_from_pickle(cls, file, key):
        try:
            cache = cls.file_cache.get(str(file))
            if not cache:
                with open(file, 'rb') as f:
                    cache = pickle.load(f)
                    cls.file_cache[str(file)] = cache
            return cache.get(key)
        except FileNotFoundError:
            return None

    @staticmethod
    def dump_pickle(file, **data):
        """Store data in a pickle file."""
        with open(file, 'wb') as f:
            pickle.dump(data, f)

    @classmethod
    def update_model(cls, model_name, model_id):
        cls._model_name = model_name
        cls.dump_pickle(file=cls.models_file, model_id=model_id)
        cls.pieces_client.model_name = model_name

    @classmethod
    def startup(cls):
        if cls.pieces_client.is_pieces_running():
            cls.version_check()  # Check the version first
        else:
            server_startup_failed()
            sys.exit(2)  # Exit the program

    @classmethod
    def version_check(cls):
        """Check if the version of PiecesOS is compatible"""
        cls.pieces_os_version = cls.pieces_client.version
        result = VersionChecker(
            cls.PIECES_OS_MIN_VERSION, cls.PIECES_OS_MAX_VERSION, cls.pieces_os_version).version_check()

        # Check compatibility
        if result.update == UpdateEnum.Plugin:
            print(
                "Please update your cli-agent tool. It is not compatible with the current PiecesOS version")
            print()
            print("https://pypi.org/project/pieces-cli/")
            print()
            print_version_details(cls.pieces_os_version, __version__)
            sys.exit(2)
        elif result.update == UpdateEnum.PiecesOS:
            print(
                "Please update PiecesOS. It is not compatible with the current cli-agent version")
            print()
            print_pieces_os_link()
            print()
            print_version_details(cls.pieces_os_version, __version__)
            sys.exit(2)

    @classmethod
    def show_error(cls, error, error_message=None):
        print()
        print(f"\033[31m{error}\033[0m")
        print(f"\033[31m{error_message}\033[0m") if error_message else None
        print()
        if not cls.run_in_loop:
            sys.exit(2)

    @classmethod
    def get_os_id(cls):
        from pieces_os_client.models.application_name_enum import ApplicationNameEnum
        if cls._os_id:
            return cls._os_id
        for app in cls.api_client.applications_api.applications_snapshot().iterable:
            if app.name == ApplicationNameEnum.OS_SERVER:
                cls._os_id = app.id
                return app.id

    @classmethod
    def open_website(cls, url: str):
        from .auth.auth_user import AuthUser
        if (not cls.api_client.is_pos_stream_running) and ("pieces.app" not in url):
            return webbrowser.open(url)
        para = {}
        if AuthUser.user_profile:
            para["user"] = AuthUser.user_profile.id
        _id = cls.get_os_id()
        if _id:
            para["os"] = _id

        url_parts = list(urlparse(url))
        query = dict(parse_qsl(url_parts[4]))
        query.update(para)

        url_parts[4] = urlencode(query)
        new_url = urlunparse(url_parts)
        print(new_url)
        webbrowser.open(new_url)
