import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.settings import Settings


class LoginCommand(BaseCommand):
    """Command to login to PiecesOS."""

    def get_name(self) -> str:
        return "login"

    def get_help(self) -> str:
        return "Login to PiecesOS"

    def get_description(self) -> str:
        return "Authenticate with PiecesOS to enable cloud features, sync across devices, and access your personal workspace"

    def get_examples(self) -> list[str]:
        return ["pieces login"]

    def get_docs(self) -> str:
        return URLs.CLI_LOGIN_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Login command has no additional arguments."""
        pass

    def execute(self, **kwargs) -> int:
        """Execute the login command."""
        try:
            Settings.pieces_client.user.login()
        except Exception as e:
            Settings.logger.error(f"Login failed: {e}")
        return 0


class LogoutCommand(BaseCommand):
    """Command to logout from PiecesOS."""

    def get_name(self) -> str:
        return "logout"

    def get_help(self) -> str:
        return "Logout from PiecesOS"

    def get_description(self) -> str:
        return "Sign out from your PiecesOS account, disabling cloud sync and returning to local-only operation"

    def get_examples(self) -> list[str]:
        return ["pieces logout"]

    def get_docs(self) -> str:
        return URLs.CLI_LOGOUT_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Logout command has no additional arguments."""
        pass

    def execute(self, **kwargs) -> int:
        """Execute the logout command."""
        try:
            Settings.pieces_client.user.logout()
        except Exception as e:
            Settings.logger.error(f"Logout failed: {e}")
        return 0
