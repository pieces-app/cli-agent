import pydoc
from typing import Optional
from pieces.settings import Settings
from rich.console import Console
from rich.markdown import Markdown
from pieces.gui import show_error
from pieces.wrapper.basic_identifier.chat import BasicChat


def conversation_handler(**kwargs):
    """Handle the conversation command"""
    
    idx = kwargs.get("CONVERSATION_INDEX",None) 
    rename = kwargs.get("rename",False)
    delete = kwargs.get("delete",False)
    chat:BasicChat

    # Check if the conversation is not empty 
    if not Settings.pieces_client.copilot.chat and (rename or delete) and not idx:
        show_error("Error in rename/delete","You can rename/delete an empty conversation")
        return 
    else:
        if idx:
            chat = Settings.pieces_client.copilot.chats()[idx]  
        else:
            chat = Settings.pieces_client.copilot.chat



    # Rename the conversation
    if rename:
        if rename == True:
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
            show_error("The conversation is empty","Please enter a conversation index, or use the ask command to ask a question.")
    else:
        get_conversation_messages(idx)


def get_conversations(**kwargs):
    """This function is used to print all conversation avaiable"""
    
    # TODO Enhance the looking using prompt toolkit
    
    conversations = Settings.pieces_client.copilot.chats()

    readable = conversations[0].updated_at

    output = f"            {readable}\n"
    for idx,conversation in enumerate(conversations,1):
        if conversation.updated_at != readable: # if new date print it to group them
            readable = conversation.updated_at
            output += f"___________________________________________\n\n            {readable}\n"


        conversation_str = f"{idx}. {conversation.name} \n"
        # Check if we are using this conversation
        if Settings.pieces_client.copilot.chat == conversation:
            output += f"\033[92m  * {conversation_str} \033[0m"
        else:
            output += conversation_str
    
    # print the pager
    pydoc.pager(output)



def get_conversation_messages(idx:Optional[int]=None,conversation:Optional[BasicChat]=None):
    """Print a conversation messages. you need to pass the index of the conversation or the conversation id"""
    
    if idx:
        conversation = Settings.pieces_client.copilot.chats()[idx]


    Settings.pieces_client.copilot.chat = conversation # change the conversation that the ask is using
    
    
    console = Console()
    for message in conversation.messages():
        console.print(message.role +": ", style="bold italic") # make the role bold and italic 
        if message.raw_content:
            md = Markdown(message.raw_content)
            console.print(md)

