import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.settings import Settings


class LoginCommand(BaseCommand):
    """Command to login to PiecesOS."""

    def get_name(self) -> str:
        return "login"

    def get_help(self) -> str:
        return "Sign into PiecesOS"

    def get_description(self) -> str:
        return "Authenticate with PiecesOS to enable cloud features, and access your personal domain, long term memory"

    def get_examples(self) -> list[str]:
        return ["pieces login"]

    def get_docs(self) -> str:
        return URLs.CLI_LOGIN_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Login command has no additional arguments."""
        pass

    def execute(self, **kwargs) -> int:
        """Execute the login command."""
        Settings.pieces_client.user.user_profile =  Settings.pieces_client.user_api.user_snapshot().user
        if Settings.pieces_client.user.user_profile:
            Settings.logger.print(f"Signed in as {Settings.pieces_client.user.name}\nemail: {Settings.pieces_client.user.email}")
            return 0
        try:
            Settings.pieces_client.user.login(True)
        except Exception as e:
            Settings.logger.error(f"Sign in failed: {e}")
        return 0


class LogoutCommand(BaseCommand):
    """Command to logout from PiecesOS."""

    def get_name(self) -> str:
        return "logout"

    def get_help(self) -> str:
        return "Sign out from PiecesOS"

    def get_description(self) -> str:
        return "Sign out from your PiecesOS account, disabling the use of any of the Pieces features"

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
            Settings.logger.error(f"Sign out failed: {e}")
        return 0
