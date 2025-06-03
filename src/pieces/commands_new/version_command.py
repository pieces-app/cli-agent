import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.settings import Settings
from pieces import __version__
from pieces.gui import print_version_details


class VersionCommand(BaseCommand):
    """Command to display version information for Pieces CLI and PiecesOS."""
    
    def get_name(self) -> str:
        return "version"
    
    def get_help(self) -> str:
        return "Gets version of PiecesOS"
    
    def get_description(self) -> str:
        return "Display version information for both Pieces CLI and PiecesOS, including build numbers and compatibility details"
    
    def get_examples(self) -> list[str]:
        return ["pieces version"]
    
    def get_docs(self) -> str:
        return URLs.CLI_VERSION_DOCS.value
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        """Version command has no additional arguments."""
        pass
    
    def execute(self, **kwargs) -> int:
        """Execute the version command."""
        if Settings.pieces_os_version:
            print_version_details(Settings.pieces_os_version, __version__)
        else:
            pass
        return 0 