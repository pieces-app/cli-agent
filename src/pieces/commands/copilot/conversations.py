import pydoc
import pieces_os_client as pos_client
from pieces.api.config import api_client



def get_conversations():
    api_instance = pos_client.ConversationsApi(api_client)
    api_response = api_instance.conversations_snapshot()
    pydoc.pager("\n".join([f"{idx}. {conversation.name}" for idx,conversation in enumerate(api_response.iterable,1)]))

