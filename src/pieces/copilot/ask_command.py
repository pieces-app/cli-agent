from typing import TYPE_CHECKING
from pieces.settings import Settings
import os
import threading

from rich.live import Live
from rich.markdown import Markdown

from pieces.wrapper.basic_identifier.chat import BasicChat
from pieces.wrapper.websockets.ask_ws import AskStreamWS

if TYPE_CHECKING:
    from pieces_os_client.models.qgpt_stream_output import QGPTStreamOutput


class AskStream:
    def __init__(self):
        self.message_compeleted = threading.Event()

    def on_message(self, response: "QGPTStreamOutput"):
        """Handle incoming websocket messages."""
        try:
            if response.question:
                answers = response.question.answers.iterable

                for answer in answers:
                    text = answer.text
                    self.final_answer += text
                    if text:
                        self.live.update(
                            Markdown(self.final_answer), refresh=True)

            if response.status == 'COMPLETED':
                self.live.update(Markdown(self.final_answer), refresh=True)
                self.live.stop()

                self.message_compeleted.set()
                Settings.pieces_client.copilot.chat = BasicChat(
                    response.conversation)

        except Exception as e:
            print(f"Error processing message: {e}")

    def add_context(self, files, assets_index):

        context = Settings.pieces_client.copilot.context

        # Files
        if files:
            for file in files:
                if file == "/" or ".":
                    context.paths.append(os.getcwd())
                    continue
                if os.path.exists(file):  # check if file exists
                    Settings.show_error(
                        f"{file} is not found", "Please enter a valid file path")
                    return

                # Return the abs path
                context.paths.append(os.path.abspath(file))
        # snippets
        if assets_index:
            for snippet in assets_index:
                try:
                    # we began enumerating from 1
                    asset = Settings.pieces_client.assets()[snippet-1]
                except KeyError:
                    return Settings.show_error("Asset not found", "Enter a vaild asset index")
                context.assets.append(asset)

    def ask(self, query, **kwargs):
        Settings.pieces_client.copilot.ask_stream_ws.on_message_callback = self.on_message
        Settings.get_model()  # Ensure the model is loaded
        files = kwargs.get("files", None)
        assets_index = kwargs.get("materials", None)
        self.add_context(files, assets_index)

        self.final_answer = ""
        self.live = Live()
        self.live.start(refresh=True)  # Start the live

        Settings.pieces_client.copilot.stream_question(query)

        finishes = self.message_compeleted.wait(Settings.TIMEOUT)
        self.message_compeleted.clear()

        if not Settings.run_in_loop:
            AskStreamWS.instance.close()  # Close the websocket if we are not run in loop

        if not finishes and not self.live:
            raise ConnectionError("Failed to get the reponse back")
        return self.final_answer
