from pieces.commands import commands_functions
from pieces.api.pieces_websocket import WebSocketManager
from pieces_os_client import *
from pieces.api.config import api_client
import os

ws_manager = WebSocketManager()
def ask(query, **kwargs):
    relevant = {"iterable":[]}
    file = kwargs.get("file")
    if file:
        if not os.path.isabs(file):
            file = os.path.abspath(file)
        relevant = QGPTApi(api_client).relevance(
            QGPTRelevanceInput(
                            query=query,
                            paths=file,
                            application=commands_functions.application.id,
                            model=commands_functions.model_id
                        ))
        
    ws_manager.ask_question(commands_functions.model_id, query,relevant=relevant)

    