from typing import Optional

import pieces._vendor.pieces_os_client
import pieces._vendor.pieces_os_client.exceptions
from rich.console import Console
from rich.text import Text
from rich.markdown import Markdown

from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
from pieces.settings import Settings


def conversation_handler(**kwargs):
    """Handle the conversation command"""

    idx = kwargs.get("CONVERSATION_INDEX", None)
    rename = kwargs.get("rename", False)
    delete = kwargs.get("delete", False)
    chat: BasicChat

    # Check if the conversation is not empty
    if not Settings.pieces_client.copilot.chat and (rename or delete) and not idx:
        Settings.show_error("Error in rename/delete",
                            "You can rename/delete an empty chat")
        return
    else:
        if idx:
            try:
                chat = Settings.pieces_client.copilot.chats()[idx-1]
            except IndexError:
                Settings.show_error("Error in chat index",
                                    "Please enter a valid chat index.")
        else:
            chat = Settings.pieces_client.copilot.chat

    # Rename the conversation
    if rename:
        if rename == True:  # noqa: E712
            con = Settings.pieces_client.conversation_api.conversation_specific_conversation_rename(
                conversation=chat._id)
            print(f"Renamed the chat to {con.name}")
        else:
            chat.name = rename
            print("Renamed the chat successfully")
        return

    # Delete the conversation
    if delete:
        r = Settings.logger.confirm(f"Are you sure you want to delete '{chat.name}'?")
        if r:
            chat.delete()
            print("Chat deleted successfully")
        return

    # Check if we want to create a new conversatiaon
    if kwargs.get("new", False):
        Settings.pieces_client.copilot.chat = None
        print("New chat created successfully")
        return

    # If the index is not given we get the conversation that we are using in the ask websocket.
    if not idx:
        if Settings.pieces_client.copilot.chat:
            get_conversation_messages(
                conversation=Settings.pieces_client.copilot.chat)
        else:
            # Show error if no conversation in the ask show error
            Settings.show_error(
                "The chat is empty", "Please enter a chat index, or use the ask command to ask a question.")
    else:
        get_conversation_messages(idx - 1)


def get_conversations(max_chats, **kwargs):
    """This function is used to print all conversations available"""
    console = Console()
    conversations = Settings.pieces_client.copilot.chats()

    if not conversations:
        console.print("No chat available.", style="bold red")
        return

    readable = conversations[0].updated_at
    output = Text(f"            {readable}\n", style="bold")

    try:
        copilot_chat = Settings.pieces_client.copilot.chat
        copilot_chat.name  # This will throw an exception if the chat is not found
    except (pieces._vendor.pieces_os_client.exceptions.NotFoundException, AttributeError):
        Settings.pieces_client.copilot.chat = None
        copilot_chat = None

    for idx, conversation in enumerate(conversations[:max_chats], 1):
        conversation_str = f"{idx}. {conversation.name}"
        summary_str = conversation.summary

        if copilot_chat == conversation:
            output.append(f"  * {conversation_str}\n", style="bold green")
        else:
            output.append(f"  {conversation_str}\n")
        if summary_str:
            if len(summary_str) > 60:
                truncated_summary = summary_str[:57] + "..."
            else:
                # If the string is 20 characters or less, use it as is
                truncated_summary = summary_str
            summary = "\n  ".join(truncated_summary.split("\n")) + "\n"
            output.append(f'  {summary}', style="dim")

    console.print(output)


def get_conversation_messages(idx: Optional[int] = None, conversation: Optional[BasicChat] = None):
    """Print a conversation messages. you need to pass the index of the conversation or the conversation id"""

    if idx is not None:
        conversation = Settings.pieces_client.copilot.chats()[idx]

    # change the conversation that the ask is using
    Settings.pieces_client.copilot.chat = conversation

    console = Console()
    for message in conversation.messages():
        # make the role bold and italic
        console.print(message.role + ": ", style="bold italic")
        if message.raw_content:
            md = Markdown(message.raw_content)
            console.print(md)
