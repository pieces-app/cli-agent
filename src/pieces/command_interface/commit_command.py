import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.autocommit import git_commit
from pieces.settings import Settings
from pieces.help_structure import HelpBuilder


class CommitCommand(BaseCommand):
    """Command to auto-generate git commits."""

    def get_name(self) -> str:
        return "commit"

    def get_help(self) -> str:
        return "Auto-generate a GitHub commit message and commit changes"

    def get_description(self) -> str:
        return "Automatically generate meaningful commit messages based on your code changes using AI, with options to stage files, add issue references, and push to remote"

    def get_examples(self):
        """Return structured examples for the commit command."""
        builder = HelpBuilder()

        # Basic commit
        builder.section(
            header="Basic Commit:", command_template="pieces commit [OPTIONS]"
        ).example("pieces commit", "Generate commit message for staged changes")

        # Advanced options
        builder.section(
            header="Advanced Options:", command_template="pieces commit [FLAGS]"
        ).example("pieces commit --all", "Stage all changes and commit").example(
            "pieces commit --push", "Commit and push to remote"
        ).example("pieces commit --issues", "Include issue references").example(
            "pieces commit -a -p", "Stage all changes and push"
        )

        return builder.build()

    def get_docs(self) -> str:
        return URLs.CLI_COMMIT_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add commit-specific arguments."""
        parser.add_argument(
            "-p",
            "--push",
            dest="push",
            action="store_true",
            help="Push the code to GitHub",
        )
        parser.add_argument(
            "-a",
            "--all",
            dest="all_flag",
            action="store_true",
            help="Stage all the files before committing",
        )
        parser.add_argument(
            "-i",
            "--issues",
            dest="issue_flag",
            action="store_true",
            help="Add issue number in the commit message",
        )

    def execute(self, **kwargs) -> int:
        """Execute the commit command."""
        try:
            git_commit(**kwargs)
            return 0
        except ConnectionError as e:
            Settings.logger.console_error.print(f"Failed to connect to PiecesOS: {e}")
            return 1
        except Exception as e:
            Settings.logger.console_error.print(f"Unexpected error during commit: {e}")
            return 3
