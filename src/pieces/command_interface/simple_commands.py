import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.core import (
    loop,
    feedback as feedback_func,
    contribute as contribute_func,
    onboarding_command,
    PiecesInstaller,
)
from pieces.core.execute_command import ExecuteCommand as CoreExecute
from pieces.gui import print_version_details
from pieces import __version__
from pieces.settings import Settings


class RunCommand(BaseCommand):
    """Command to run CLI in interactive loop mode."""

    def get_name(self) -> str:
        return "run"

    def get_help(self) -> str:
        return "Runs CLI in a loop"

    def get_description(self) -> str:
        return "Run the Pieces CLI in interactive loop mode, allowing you to execute multiple commands sequentially without restarting the CLI"

    def get_examples(self) -> list[str]:
        return ["pieces run"]

    def get_docs(self) -> str:
        return URLs.CLI_RUN_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        loop(**kwargs)
        return 0


class ExecuteCommand(BaseCommand):
    """Command to execute shell/bash materials."""

    def get_name(self) -> str:
        return "execute"

    def get_help(self) -> str:
        return "Execute shell or bash materials"

    def get_description(self) -> str:
        return "Execute shell or bash code snippets directly from your saved materials, making it easy to run saved scripts and commands"

    def get_examples(self) -> list[str]:
        return ["pieces execute"]

    def get_docs(self) -> str:
        return URLs.CLI_EXECUTE_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        CoreExecute.execute_command(**kwargs)
        return 0


class FeedbackCommand(BaseCommand):
    """Command to submit feedback."""

    def get_name(self) -> str:
        return "feedback"

    def get_help(self) -> str:
        return "Submit feedback"

    def get_description(self) -> str:
        return "Submit feedback, bug reports, or feature requests to help improve the Pieces CLI. Your feedback is invaluable for making the tool better"

    def get_examples(self) -> list[str]:
        return ["pieces feedback"]

    def get_docs(self) -> str:
        return URLs.CLI_FEEDBACK_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        feedback_func(**kwargs)
        return 0


class ContributeCommand(BaseCommand):
    """Command to learn how to contribute."""

    def get_name(self) -> str:
        return "contribute"

    def get_help(self) -> str:
        return "How to contribute"

    def get_description(self) -> str:
        return "Learn how to contribute to the Pieces CLI project, including guidelines for submitting pull requests, reporting issues, and improving documentation"

    def get_examples(self) -> list[str]:
        return ["pieces contribute"]

    def get_docs(self) -> str:
        return URLs.CLI_CONTRIBUTE_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        contribute_func(**kwargs)
        return 0


class InstallCommand(BaseCommand):
    """Command to install PiecesOS."""

    def get_name(self) -> str:
        return "install"

    def get_help(self) -> str:
        return "Install PiecesOS"

    def get_description(self) -> str:
        return "Install or update PiecesOS, the local runtime that powers all Pieces applications. This command will download and set up PiecesOS for your platform"

    def get_examples(self) -> list[str]:
        return ["pieces install"]

    def get_docs(self) -> str:
        return URLs.CLI_INSTALL_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        PiecesInstaller().run()
        return 0


class OnboardingCommand(BaseCommand):
    """Command to start onboarding process."""

    def get_name(self) -> str:
        return "onboarding"

    def get_help(self) -> str:
        return "Start the onboarding process"

    def get_description(self) -> str:
        return "Start the interactive onboarding process to set up Pieces CLI, configure settings, and learn about key features through a guided tutorial"

    def get_examples(self) -> list[str]:
        return ["pieces onboarding"]

    def get_docs(self) -> str:
        return URLs.CLI_ONBOARDING_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        onboarding_command(**kwargs)
        return 0


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
