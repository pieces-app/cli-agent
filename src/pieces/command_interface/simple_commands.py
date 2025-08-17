import argparse
from urllib3.exceptions import MaxRetryError
from pieces.base_command import BaseCommand
from pieces.headless.models.base import CommandResult
from pieces.headless.models.version import create_version_success
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
from pieces.help_structure import HelpBuilder


class RunCommand(BaseCommand):
    """Command to run CLI in interactive loop mode."""

    def get_name(self) -> str:
        return "run"

    def get_help(self) -> str:
        return "Runs CLI in a loop"

    def get_description(self) -> str:
        return "Run the Pieces CLI in interactive loop mode, allowing you to execute multiple commands sequentially without restarting the CLI"

    def get_examples(self):
        """Return structured examples for the run command."""
        builder = HelpBuilder()

        builder.section(
            header="Interactive Mode:", command_template="pieces run"
        ).example("pieces run", "Start interactive CLI loop mode")

        return builder.build()

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

    def get_examples(self):
        """Return structured examples for the execute command."""
        builder = HelpBuilder()

        builder.section(
            header="Execute Code:", command_template="pieces execute"
        ).example("pieces execute", "Execute code from selected material")

        return builder.build()

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

    def get_examples(self):
        """Return structured examples for the feedback command."""
        builder = HelpBuilder()

        builder.section(
            header="Submit Feedback:", command_template="pieces feedback"
        ).example(
            "pieces feedback", "Submit feedback, bug reports, or feature requests"
        )

        return builder.build()

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

    def get_examples(self):
        """Return structured examples for the contribute command."""
        builder = HelpBuilder()

        builder.section(
            header="Contribution Info:", command_template="pieces contribute"
        ).example("pieces contribute", "Learn how to contribute to Pieces CLI project")

        return builder.build()

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

    def get_examples(self):
        """Return structured examples for the install command."""
        builder = HelpBuilder()

        builder.section(
            header="Install PiecesOS:", command_template="pieces install"
        ).example("pieces install", "Install or update PiecesOS runtime")

        return builder.build()

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

    def get_examples(self):
        """Return structured examples for the onboarding command."""
        builder = HelpBuilder()

        builder.section(
            header="Getting Started:", command_template="pieces onboarding"
        ).example("pieces onboarding", "Start interactive setup and tutorial")

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_ONBOARDING_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        onboarding_command(**kwargs)
        return 0


class VersionCommand(BaseCommand):
    """Command to display version information for Pieces CLI and PiecesOS."""

    support_headless = True

    def get_name(self) -> str:
        return "version"

    def get_help(self) -> str:
        return "Gets version of PiecesOS"

    def get_description(self) -> str:
        return "Display version information for both Pieces CLI and PiecesOS, including build numbers and compatibility details"

    def get_examples(self):
        """Return structured examples for the version command."""
        builder = HelpBuilder()

        builder.section(
            header="Version Information:", command_template="pieces version"
        ).example("pieces version", "Display CLI and PiecesOS version info")

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_VERSION_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Version command has no additional arguments."""
        pass

    def execute(self, **kwargs) -> CommandResult:
        """Execute the version command."""
        if Settings.pieces_os_version:
            print_version_details(Settings.pieces_os_version, __version__)
        else:
            pass
        return CommandResult(
            0, create_version_success(__version__, Settings.pieces_os_version)
        )


class RestartPiecesOSCommand(BaseCommand):
    """Command to restart PiecesOS."""

    def get_name(self) -> str:
        return "restart"

    def get_help(self) -> str:
        return "Restart PiecesOS"

    def get_description(self) -> str:
        return "Restart the PiecesOS"

    def get_examples(self):
        """Return structured examples for the restart command."""
        builder = HelpBuilder()

        builder.section(
            header="Restart Service:", command_template="pieces restart"
        ).example("pieces restart", "Restart PiecesOS service")

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_RESTART_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        try:
            Settings.pieces_client.os_api.os_restart()
        except MaxRetryError:
            pass
        if Settings.pieces_client.is_pieces_running(15):
            Settings.logger.print("[green]PiecesOS restarted successfully.")
            return 0
        else:
            Settings.logger.print(
                "[red]Failed to restart PiecesOS. Please run `pieces open`."
            )
        return 1
