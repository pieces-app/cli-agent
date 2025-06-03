import argparse
from pieces.base_command import BaseCommand
from pieces.urls import URLs
from pieces.copilot import get_conversations, conversation_handler


class ChatsCommand(BaseCommand):
    """Command to list all conversations/chats."""

    def get_name(self) -> str:
        return "chats"

    def get_aliases(self) -> list[str]:
        return ["conversations"]

    def get_help(self) -> str:
        return "Print all chats"

    def get_description(self) -> str:
        return "Display a list of all your saved conversations with the Pieces Copilot, showing titles and timestamps for easy navigation"

    def get_examples(self) -> list[str]:
        return ["pieces chats", "pieces chats 20", "pieces conversations"]

    def get_docs(self) -> str:
        return URLs.CLI_CHATS_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add chats-specific arguments."""
        parser.add_argument(
            "max_chats",
            nargs="?",
            type=int,
            default=10,
            help="Max number of chats to show",
        )

    def execute(self, **kwargs) -> int:
        """Execute the chats command."""
        get_conversations(**kwargs)
        return 0


class ChatCommand(BaseCommand):
    """Command to manage individual conversations."""

    def get_name(self) -> str:
        return "chat"

    def get_aliases(self) -> list[str]:
        return ["conversation"]

    def get_help(self) -> str:
        return "Select a chat"

    def get_description(self) -> str:
        return "Manage individual conversations with the Pieces Copilot. You can select, create, rename, or delete conversations"

    def get_examples(self) -> list[str]:
        return [
            "pieces chat",
            "pieces chat 1",
            "pieces chat --new",
            "pieces chat --rename 'New Title'",
            "pieces chat --delete",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_CHAT_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        """Add chat-specific arguments."""
        parser.add_argument(
            "CONVERSATION_INDEX",
            type=int,
            nargs="?",
            default=None,
            help="Index of the chat if None it will get the current conversation.",
        )
        parser.add_argument(
            "-n", "--new", action="store_true", dest="new", help="Create a new chat"
        )
        parser.add_argument(
            "-r",
            "--rename",
            dest="rename",
            nargs="?",
            const=True,
            help="Rename the conversation that you are currently. If nothing is specified it will rename the current chat using the llm model",
        )
        parser.add_argument(
            "-d",
            "--delete",
            action="store_true",
            dest="delete",
            help="Delete the chat that you are currently using in the ask command",
        )

    def execute(self, **kwargs) -> int:
        """Execute the chat command."""
        conversation_handler(**kwargs)
        return 0
