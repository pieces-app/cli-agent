from typing import TYPE_CHECKING
from pieces.settings import Settings
import os
import threading

from rich.live import Live
from rich.markdown import Markdown

from pieces.gui import show_error

if TYPE_CHECKING:
    from pieces_os_client.models.qgpt_stream_output import QGPTStreamOutput


class AskStream:
    def __init__(self):
        self.message_compeleted = threading.Event()

        
    def on_message(self,ws, response:"QGPTStreamOutput"):
        """Handle incoming websocket messages."""
        try:
            if response.question:
                answers = response.question.answers.iterable

                for answer in answers:
                    text = answer.text
                    self.final_answer += text
                    if text:
                        self.live.update(Markdown(self.final_answer))

            if response.status == 'COMPLETED':
                self.live.update(Markdown(self.final_answer), refresh=True)
                self.live.stop()
 

                self.conversation = response.conversation

                self.message_compeleted.set()

        except Exception as e:
            print(f"Error processing message: {e}")


    def add_context(self,files,assets_index):
        
        context = Settings.pieces_client.copilot.context

        # Files
        if files:
            for file in files:
                if file == "/" or ".":
                    context.paths.append(os.getcwd())
                    continue
                if os.path.exists(file): # check if file exists
                    show_error(f"{file} is not found","Please enter a valid file path")
                    return
                
                context.paths.append(os.path.abspath(file)) # Return the abs path
        # snippets
        if assets_index:
            for snippet in assets_index:
                try: asset = Settings.pieces_client.assets()[snippet-1] # we began enumerating from 1
                except KeyError: return show_error("Asset not found","Enter a vaild asset index")
                context.assets.append(asset)

    def ask(self,query, **kwargs):
        files = kwargs.get("files",None)
        assets_index = kwargs.get("snippets",None)
        self.add_context(files,assets_index)

        self.final_answer = ""
        self.live = Live()
        self.live.start(refresh=True)  # Start the live

        Settings.pieces_client.copilot.stream_question(query)

        finishes = self.message_compeleted.wait(Settings.TIMEOUT)
        self.message_compeleted.clear()

        if not finishes and not self.live:
            raise ConnectionError("Failed to get the reponse back")
        return self.final_answer