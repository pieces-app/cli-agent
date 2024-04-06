import pydoc
import pieces_os_client as pos_client
from pieces.api.config import api_client
from rich.console import Console
from rich.markdown import Markdown
from pieces.gui import show_error
from .ask_command import ws_manager

conversation_map = {}

def conversation_handler(**kwargs):
    """Handle the conversation command"""
    
    idx = kwargs.get("CONVERSATION_INDEX",None) 

    # Check if we want to create a new conversatiaon
    if kwargs.get("new",False):
        ws_manager.conversation = None
        return
    
    # If the index is not given we get the conversation that we are using in the ask websocket.
    if not idx:
        if ws_manager.conversation:
            get_conversation_messages(conversation_id = ws_manager.conversation)
        else:
            # Show error if no conversation in the ask show error
            show_error("The conversation is empty","Please enter a conversation index.")
    else:
        get_conversation_messages(idx)


def get_conversations(**kwargs):
    """This function is used to print all conversation avaiable"""
    global conversation_map
    api_instance = pos_client.ConversationsApi(api_client)
    api_response = api_instance.conversations_snapshot()

    # Sort the dictionary by the "updated" timestamp
    sorted_conversations = sorted(api_response.iterable, key=lambda x: x.updated.value, reverse=True)

    readable = sorted_conversations[0].updated.readable
    output = f"            {readable}\n"
    for idx,conversation in enumerate(sorted_conversations,1):
        if conversation.updated.readable != readable: # if new date print it to group them
            readable = conversation.updated.readable
            output += f"__________________________________________________\n\n            {readable}\n"
        
        if not conversation.name:
            conversation.name = "New conversation"

        conversation_str = f"{idx}. {conversation.name}"
        # Check if we are using this conversation
        if ws_manager.conversation == conversation.id:
            output += f"\033[92m  *{conversation_str} \n \033[0m"
        else:
            output += conversation_str
    
    # print the pager
    pydoc.pager(output)



def get_conversation_messages(idx:int=None,conversation_id=None):
    """Print a conversation messages. you need to pass the index of the conversation or the conversation id"""
    global conversation_map
    conversation_api = pos_client.ConversationApi(api_client)
    message_api = pos_client.ConversationMessageApi(api_client)
    if not conversation_id:
        
        if not conversation_map:
            conversations_api = pos_client.ConversationsApi(api_client)
            api_response = conversations_api.conversations_snapshot()
            # Sort the dictionary by the "updated" timestamp
            sorted_conversations = sorted(api_response.iterable, key=lambda x: x.updated.value, reverse=True)

            conversation_map = {idx: conversation.id for idx,conversation in enumerate(sorted_conversations,start=1)}

        conversation_id = conversation_map[idx]
    
    conversation:pos_client.Conversation = conversation_api.conversation_get_specific_conversation(conversation=conversation_id)
    
    
    ws_manager.conversation = conversation.id # change the conversation that the ask is using
    
    
    console = Console()
    for key,val in conversation.messages.indices.items():
        if val == -1: # message is deleted
            continue
        message = message_api.message_specific_message_snapshot(message=key)
        console.print(message.role+"\n\n", style="u b") # underline and make it bold the role
        if message.fragment.string:
            md = Markdown(message.fragment.string.raw)
            console.print(md)
        
        console.print("__________________________________________________")
        

