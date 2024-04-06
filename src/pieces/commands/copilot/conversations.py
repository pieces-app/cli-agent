import pydoc
import pieces_os_client as pos_client
from pieces.api.config import api_client



def conversation_handler(**kwargs):
    get_conversations()


def get_conversations():
    api_instance = pos_client.ConversationsApi(api_client)
    api_response = api_instance.conversations_snapshot()

    # Sort the dictionary by the "updated" timestamp
    sorted_conversations = sorted(api_response.iterable, key=lambda x: x.updated.value, reverse=True)

    
    readable = sorted_conversations[0].updated.readable
    conversations_str = f"            {readable}\n"
    for idx,conversation in enumerate(sorted_conversations,1):
        if conversation.updated.readable != readable:
            readable = conversation.updated.readable
            conversations_str += f"__________________________________________________\n\n            {readable}\n"
        if not conversation.name:
            conversation.name = "New conversation"
        conversations_str += f"{idx}. {conversation.name}\n"
        
    pydoc.pager(conversations_str)


