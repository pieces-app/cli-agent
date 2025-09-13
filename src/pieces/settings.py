import os
import sys
from rich.progress import Progress, TextColumn, SpinnerColumn
import sentry_sdk

from pieces.config.constants import (
    CLI_CONFIG_PATH,
    MODEL_CONFIG_PATH,
    MCP_CONFIG_PATH,
    USER_CONFIG_PATH,
)
from pieces.headless.exceptions import HeadlessCompatibilityError
from pieces.logger import Logger
from pieces._vendor.pieces_os_client.wrapper import PiecesClient
from pieces._vendor.pieces_os_client.wrapper.version_compatibility import (
    VersionChecker,
    UpdateEnum,
)
from pieces import __version__
from pieces.gui import (
    print_version_details,
)
from pieces.urls import URLs
from pieces.config.constants import PIECES_DATA_DIR
from pieces.config.managers import (
    CLIManager,
    ModelManager,
    MCPManager,
    UserManager,
)


class Settings:
    """Settings class for the PiecesCLI"""

    pieces_client = PiecesClient()

    PIECES_OS_MIN_VERSION = "12.0.0"  # Minimum version (12.0.0)
    PIECES_OS_MAX_VERSION = "13.0.0"  # Maximum version (13.0.0)

    TIMEOUT = 40  # Websocket ask timeout

    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    cli_config = CLIManager(CLI_CONFIG_PATH)
    model_config = ModelManager(MODEL_CONFIG_PATH)
    mcp_config = MCPManager(MCP_CONFIG_PATH)
    user_config = UserManager(USER_CONFIG_PATH)

    logger = Logger(log_dir=PIECES_DATA_DIR)  # Will be set on the app startup

    _os_id = None

    run_in_loop = False  # is CLI looping?
    headless_mode: bool = False  # is CLI running in headless mode?

    open_snippet_dir = os.path.join(PIECES_DATA_DIR, "opened_snippets")

    @classmethod
    def startup(cls, bypass_login=False):
        if cls.pieces_client.is_pieces_running():
            cls.version_check()  # Check the version first
            if not bypass_login:
                # All of that needs the user to be logged in
                cls.check_login()
                model_info = Settings.model_config.model
                if model_info:
                    cls.pieces_client.model_name = model_info.name
                os_id = cls.get_os_id()
                sentry_sdk.set_user({"id": os_id or "unknown"})
        else:
            if cls.pieces_client.is_pieces_running() or cls.open_pieces_widget():
                return cls.startup(bypass_login)
            if cls.logger.confirm(
                "Pieces OS is required but wasn’t found or couldn’t be launched.\n"
                "Do you want to install it now and get started?"
            ):
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
        if cls.pieces_os_version == "debug":
            return  # Skip version check in debug mode
        result = VersionChecker(
            cls.PIECES_OS_MIN_VERSION, cls.PIECES_OS_MAX_VERSION, cls.pieces_os_version
        ).version_check()
        if cls.headless_mode and not result.compatible:
            raise HeadlessCompatibilityError(result)

        # Check compatibility
        if result.update == UpdateEnum.Plugin:
            cls.logger.print(
                "Please update your cli-agent tool. It is not compatible with the current PiecesOS version"
            )
            cls.logger.print(
                URLs.DOCS_CLI.value
            )  # TODO: We might need to add a link a better link here
            print_version_details(cls.pieces_os_version, __version__)
            sys.exit(2)
        elif result.update == UpdateEnum.PiecesOS:
            # TODO: Use the update POS endpoint
            cls.logger.print(
                "Please update PiecesOS. It is not compatible with the current cli-agent version"
            )
            cls.logger.print(URLs.DOCS_INSTALLATION.value)
            print_version_details(cls.pieces_os_version, __version__)
            sys.exit(2)

    @classmethod
    def check_login(cls):
        user = cls.pieces_client.user_api.user_snapshot().user
        if not user:
            if cls.logger.confirm(
                "Please sign into Pieces to use this feature. Do you want to sign in now?"
            ):
                cls.pieces_client.user.login(True)
                user = cls.pieces_client.user_api.user_snapshot().user
        if user:
            return
        sys.exit(1)

    @classmethod
    def show_error(cls, error, error_message=None):
        cls.logger.console_error.print(f"[red]{error}")
        cls.logger.console_error.print(
            f"[red]{error_message}"
        ) if error_message else None
        if not cls.run_in_loop:
            sys.exit(2)

    @classmethod
    def get_os_id(cls):
        from pieces._vendor.pieces_os_client.models.application_name_enum import (
            ApplicationNameEnum,
        )

        if cls._os_id:
            return cls._os_id
        for app in cls.pieces_client.applications_api.applications_snapshot().iterable:
            if app.name == ApplicationNameEnum.OS_SERVER:
                cls._os_id = app.id
                return app.id

    @classmethod
    def open_pieces_widget(cls):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=cls.logger.console,
            transient=False,
        ) as progress:
            pos_task = progress.add_task(
                "[cyan]Launching PiecesOS...",
            )
            if cls.pieces_client.open_pieces_os():
                progress.update(pos_task, visible=False)
                return True

            progress.update(pos_task, description="[red]PiecesOS is not installed")
            return False
