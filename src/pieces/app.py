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
        Settings.logger = Logger(config.get("debug", False), Settings.pieces_data_dir)
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
            res = Settings.logger.prompt(
                "It looks like this is your first time using the Pieces CLI."
                "\nWould you like to start onboarding",
                choices=["y", "n", "skip"],
            )
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
        if command not in [
            "help",
            "--version",
            "install",
            "onboarding",
            "feedback",
            "contribute",
            "open",
        ] and not (command == "mcp" and mcp_subcommand == "start"):
            Settings.startup()
        Settings.logger.debug(f"Running command {arg} using: {args}")
        args.func(**vars(args))


def main():
    try:
        cli = PiecesCLI()
        cli.run()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        Settings.logger.critical(e)
        Settings.show_error("UNKNOWN EXCEPTION", e)
    finally:
        from pieces._vendor.pieces_os_client.wrapper.websockets.base_websocket import BaseWebsocket

        BaseWebsocket.close_all()


if __name__ == "__main__":
    main()
