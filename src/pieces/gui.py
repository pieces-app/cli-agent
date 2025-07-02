from typing import TYPE_CHECKING

from rich.markdown import Markdown
from .logger import Logger


if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.wrapper.basic_identifier.asset import (
        BasicAsset,
    )


def print(*args, **kwargs):
    return Logger.get_instance().print(*args, **kwargs)


def welcome():
    print()
    print("############################")
    print()
    print("Pieces CLI Started")
    print()
    print("############################")
    print()


def line():
    print()
    print("############################")
    print()


def double_line(text):
    print()
    print("############################")
    print()
    print(text)
    print()
    print("############################")
    print()


def print_version_details(pos_version, cli_version):
    print(Markdown(f"`PiecesOS Version:` {pos_version}"))
    print(Markdown(f"`CLI Version:` {cli_version}"))


def double_space(text):
    print()
    print(text)
    print()


def space_below(text):
    print(text)
    print()


def print_instructions():
    print()
    print("Enter command:")
    print("  'help' to see all commands")
    print("  '-h' after a command to see detailed help")
    print("  'exit' to quit")
    print()
    print("Ready...")
    line()


def print_asset_details(asset: "BasicAsset"):
    print(f"Name: {asset.name}")
    print(f"Created: {asset.created_at}")
    print(f"Updated: {asset.updated_at}")
    print(f"Type: {asset.type.value}")
    print(f"Language: {asset.classification.value}") if asset.classification else None


def deprecated(command, instead):
    """
    Decorator
        command(str): which is the command that is deprated
        instead(str): which command should we use instead
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            if kwargs.get("show_warning", True):
                print(
                    f"\033[93m WARNING: `{command}` is deprecated and will"
                    f" be removed in later versions\nPlease use `{instead}` instead \033[0m"
                )
            func(*args, **kwargs)

        return wrapper

    return decorator
