import sys
import os

from pieces.config.constants import PIECES_DATA_DIR
from pieces.config.migration import run_migration
from pieces.headless.exceptions import HeadlessError
from pieces.headless.models.base import ErrorCode
from pieces.headless.output import HeadlessOutput
from pieces.pieces_argparser import PiecesArgparser
from pieces.command_registry import CommandRegistry
from pieces.settings import Settings
from pieces.logger import Logger
from pieces import __version__
from pieces.command_interface import *  # noqa: F403


class PiecesCLI:
    def __init__(self):
        self.command: str
        self.parser = PiecesArgparser(
            description="Pieces CLI for interacting with the PiecesOS",
        )
        self.registry = CommandRegistry(self.parser)
        self.registry.setup_parser(self.parser, __version__)
        PiecesArgparser.parser = self.parser

    def _check_data_dir_permissions(self):
        """
        Check if we have read/write permissions to PIECES_DATA_DIR.

        Returns:
            True if we have read/write access, False otherwise
        """
        try:
            is_accessible = os.access(PIECES_DATA_DIR, os.R_OK | os.W_OK)
        except (PermissionError, OSError):
            is_accessible = False
        if not is_accessible:
            Settings.logger.print(
                "[red]Pieces CLI failed to access configuration files.[/red]"
            )
            Settings.logger.print(
                "[yellow]This is likely due to missing file system permissions.[/yellow]"
            )
            Settings.logger.print(
                f"[blue]Please ensure the CLI has read/write access to: {PIECES_DATA_DIR}[/blue]"
            )
            sys.exit(128)
        os.makedirs(PIECES_DATA_DIR, exist_ok=True)

    def run(self):
        self._check_data_dir_permissions()
        Settings.logger = Logger(__version__ == "dev", PIECES_DATA_DIR)

        # Run migration - we know we have permissions now
        if not run_migration():
            Settings.logger.critical("Migration failed.")
            Settings.logger.print(
                "[red]Migration failed. Please contact support@pieces.app[/red]",
            )

        if len(sys.argv) == 1:
            return self.parser.print_help()
        try:
            args = self.parser.parse_args()
        except SystemExit:
            # This occurs when argparse encounters --help, invalid args, or no command
            # In most cases, argparse has already printed appropriate messages and exited
            return

        # Check for ignore onboarding flag from parsed args
        ignore_onboarding = getattr(args, "ignore_onboarding", False)

        onboarded = Settings.user_config.onboarded

        if (
            not Settings.user_config.skip_onboarding
            and not onboarded
            and not ignore_onboarding
        ):
            Settings.logger.print(
                (
                    "👋 It looks like this is your first time using the Pieces CLI.\n\n"
                    "Would you like to start the onboarding process?\n"
                    "\n"
                    "  [y] Yes  – Start onboarding now.\n"
                    "  [n] No   – Skip for now (you'll be asked again next time).\n"
                    "  [skip]   – Don't ask me again (you can always run `pieces onboarding` manually).\n"
                ),
                markup=False,
            )

            res = Settings.logger.prompt(choices=["y", "n", "skip"], _default="n")
            if res.lower() == "y":
                return OnboardingCommand.instance.execute()  # noqa: F405
            elif res.lower() == "skip":
                Settings.user_config.skip_onboarding = True

        command = args.command
        PiecesCLI.command = command
        if not command and getattr(args, "version", False):
            command = "--version"

        mcp_subcommand = getattr(args, "mcp", None)

        # Check if the command needs PiecesOS or not
        # TODO: need some cleanups here
        if command not in [
            "help",
            "--version",
            "install",
            "onboarding",
            "feedback",
            "contribute",
            "open",
            "config",
            "completion",
        ] and not (command == "mcp" and mcp_subcommand == "start"):
            bypass_login = True if (command in ["version"]) else False
            Settings.startup(bypass_login)
        Settings.logger.debug(f"Running command {command} using: {args}")
        args.func(**vars(args))


def main():
    cli = PiecesCLI()
    try:
        cli.run()
    except (KeyboardInterrupt, EOFError):
        if Settings.headless_mode:
            HeadlessOutput.output_error(
                command=cli.command if cli else "unknown",
                error_code=ErrorCode.USER_INTERRUPTED,
                error_message="Operation cancelled by user",
            )
    except Exception as e:
        if isinstance(e, HeadlessError):
            HeadlessOutput.handle_exception(e, PiecesCLI.command or "unknown")
        elif __version__ == "dev":
            Settings.logger.console.print_exception(show_locals=True)
        elif Settings.headless_mode:
            HeadlessOutput.handle_exception(e, PiecesCLI.command or "unknown")
        else:
            Settings.logger.critical(e)
            Settings.show_error("UNKNOWN EXCEPTION", e)
    finally:
        from pieces._vendor.pieces_os_client.wrapper.websockets.base_websocket import (
            BaseWebsocket,
        )

        BaseWebsocket.close_all()


if __name__ == "__main__":
    main()
