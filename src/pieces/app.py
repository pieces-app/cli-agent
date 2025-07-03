import sys
from pieces.pieces_argparser import PiecesArgparser
from pieces.command_registry import CommandRegistry
from pieces.settings import Settings
from pieces.logger import Logger
from pieces import __version__

from pieces.command_interface import *  # noqa: F403
from pieces.core import ConfigCommands


class PiecesCLI:
    def __init__(self):
        self.parser = PiecesArgparser(
            description="Pieces CLI for interacting with the PiecesOS",
        )
        self.registry = CommandRegistry(self.parser)
        self.registry.setup_parser(self.parser, __version__)
        PiecesArgparser.parser = self.parser

    def run(self):
        config = ConfigCommands.load_config()
        Settings.logger = Logger(__version__ == "dev", Settings.pieces_data_dir)
        try:
            arg = sys.argv[1]
            if arg == "--ignore-onboarding":
                arg = sys.argv[2]
        except IndexError:  # No command provided
            self.parser.print_help()
            return

        ignore_onboarding = False
        for _arg in sys.argv:
            if _arg == "--ignore-onboarding":
                ignore_onboarding = True

        onboarded = config.get("onboarded", False)

        if (
            not config.get("skip_onboarding", False)
            and not onboarded
            and not ignore_onboarding
        ):
            res = Settings.logger.print(
                (
                    "👋 It looks like this is your first time using the Pieces CLI.\n\n"
                    "Would you like to start the onboarding process?\n"
                    "\n"
                    "  [y] Yes  – Start onboarding now.\n"
                    "  [n] No   – Skip for now (you'll be asked again next time).\n"
                    "  [skip]   – Don't ask me again (you can always run `pieces onboarding` manually).\n"
                ),
                markup=False
            )

            res = Settings.logger.prompt(choices=["y", "n", "skip"])
            if res.lower() == "y":
                return OnboardingCommand.instance.execute()  # noqa: F405
            elif res.lower() == "skip":
                config["skip_onboarding"] = True
                ConfigCommands.save_config(config)

        args = self.parser.parse_args()
        command = args.command
        if not command and args.version:
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
        Settings.logger.debug(f"Running command {arg} using: {args}")
        args.func(**vars(args))


def main():
    try:
        cli = PiecesCLI()
        cli.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        if __version__ == "dev":
            Settings.logger.console.print_exception(show_locals=True)
            return

        Settings.logger.critical(e)
        Settings.show_error("UNKNOWN EXCEPTION", e)
    finally:
        from pieces._vendor.pieces_os_client.wrapper.websockets.base_websocket import (
            BaseWebsocket,
        )

        BaseWebsocket.close_all()


if __name__ == "__main__":
    main()
