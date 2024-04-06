from pieces.commands import commands_functions
from pieces.gui import show_error


def ask(query, **kwargs):
    try:
       commands_functions.ws_manager.ask_question(commands_functions.model_id, query)
    except Exception as e:
        show_error("Error occurred while asking the question:", e)