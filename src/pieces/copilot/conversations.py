from typing import Optional

from rich.console import Console
from rich.text import Text
from rich.markdown import Markdown

from pieces.wrapper.basic_identifier.chat import BasicChat
from pieces.settings import Settings


def conversation_handler(**kwargs):
    """Handle the conversation command"""
    
    idx = kwargs.get("CONVERSATION_INDEX",None) 
    rename = kwargs.get("rename",False)
    delete = kwargs.get("delete",False)
    chat:BasicChat

    # Check if the conversation is not empty 
    if not Settings.pieces_client.copilot.chat and (rename or delete) and not idx:
        Settings.show_error("Error in rename/delete","You can rename/delete an empty conversation")
        return 
    else:
        if idx:
            try:
                chat = Settings.pieces_client.copilot.chats()[idx-1] 
            except IndexError:
                Settings.show_error("Error in conversation index","Please enter a valid conversation index.") 
        else:
            chat = Settings.pieces_client.copilot.chat



    # Rename the conversation
    if rename:
        if rename == True:  # noqa: E712
            con = Settings.pieces_client.conversation_api.conversation_specific_conversation_rename(conversation=chat._id)
            print(f"Renamed the conversation to {con.name}")
        else:
            chat.name = rename
            print("Renamed the conversation successfully")
        return

    # Delete the conversation
    if delete:
        r = input(f"Are you sure you want to delete '{chat.name}'? (y/n) : ")
        if r == "y":
            chat.delete()
            print("Conversation deleted successfully")
        return


    # Check if we want to create a new conversatiaon
    if kwargs.get("new",False):
        Settings.pieces_client.copilot.chat = None
        print("New conversation created successfully")
        return
    
    
    
    # If the index is not given we get the conversation that we are using in the ask websocket.
    if not idx:
        if Settings.pieces_client.copilot.chat:
            get_conversation_messages(conversation = Settings.pieces_client.copilot.chat)
        else:
            # Show error if no conversation in the ask show error
            Settings.show_error("The conversation is empty","Please enter a conversation index, or use the ask command to ask a question.")
    else:
        get_conversation_messages(idx - 1)

def get_conversations(max_conversations,**kwargs):
    """This function is used to print all conversations available"""
    console = Console()
    conversations = Settings.pieces_client.copilot.chats()

    if not conversations:
        console.print("No conversations available.", style="bold red")
        return

    readable = conversations[0].updated_at
    output = Text(f"            {readable}\n", style="bold")

    for idx, conversation in enumerate(conversations[:max_conversations], 1):
        conversation_str = f"{idx}. {conversation.name}"
        summary_str = conversation.summary


        if Settings.pieces_client.copilot.chat == conversation:
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


def get_conversation_messages(idx:Optional[int]=None,conversation:Optional[BasicChat]=None):
    """Print a conversation messages. you need to pass the index of the conversation or the conversation id"""

    if idx is not None:
        conversation = Settings.pieces_client.copilot.chats()[idx]


    Settings.pieces_client.copilot.chat = conversation # change the conversation that the ask is using
    
    
    console = Console()
    for message in conversation.messages():
        console.print(message.role +": ", style="bold italic") # make the role bold and italic 
        if message.raw_content:
            md = Markdown(message.raw_content)
            console.print(md)

