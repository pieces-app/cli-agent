from pieces.commands import commands_functions
from pieces.gui import show_error
from pieces.api.pieces_websocket import WebSocketManager

ws_manager = WebSocketManager()
def ask(query, **kwargs):
    try:
       ws_manager.ask_question(commands_functions.model_id, query)
    except Exception as e:
        show_error("Error occurred while asking the question:", e)