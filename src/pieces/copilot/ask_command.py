from typing import TYPE_CHECKING
from pieces.copilot.ltm import enable_ltm
from pieces.settings import Settings
import os
import threading

from rich.live import Live
from rich.markdown import Markdown

from pieces._vendor.pieces_os_client.wrapper.basic_identifier.chat import BasicChat
from pieces._vendor.pieces_os_client.wrapper.websockets.ask_ws import AskStreamWS

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.qgpt_stream_output import QGPTStreamOutput


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
                        self.live.update(Markdown(self.final_answer), refresh=True)

            if response.status == "COMPLETED":
                self.live.update(Markdown(self.final_answer), refresh=True)
                self.live.stop()

                self.message_compeleted.set()
                Settings.pieces_client.copilot.chat = BasicChat(response.conversation)

        except Exception as e:
            Settings.logger.critical(e)
            Settings.logger.print(f"Error processing message: {e}")

    def validate_file_paths(self, paths):
        """Validate and normalize file paths to prevent directory traversal attacks."""
        validated_paths = []
        current_dir = os.getcwd()

        for path in paths:
            if not path or path.isspace():
                continue

            # Expand user home directory and convert to absolute path
            abs_path = os.path.abspath(os.path.expanduser(path))

            # Ensure path doesn't escape allowed directories
            # Allow paths within current working directory or user's home directory
            home_dir = os.path.expanduser("~")
            if not (abs_path.startswith(current_dir) or abs_path.startswith(home_dir)):
                Settings.show_error(
                    f"Path '{path}' is outside allowed directories",
                    "Files must be within the current working directory or home directory",
                )
                raise ValueError(f"Path '{path}' is outside allowed directories")

            # Check if the path exists
            if not os.path.exists(abs_path):
                Settings.show_error(
                    f"Path '{path}' does not exist",
                    "Please enter a valid file or directory path",
                )
                raise ValueError(f"Path '{path}' does not exist")

            validated_paths.append(abs_path)

        return validated_paths

    def add_context(self, files, assets_index):
        context = Settings.pieces_client.copilot.context

        if files:
            try:
                validated_paths = self.validate_file_paths(files)
                for path in validated_paths:
                    context.paths.append(path)
            except ValueError:
                return

        # snippets
        if assets_index:
            for snippet in assets_index:
                try:
                    # we began enumerating from 1
                    asset = Settings.pieces_client.assets()[snippet - 1]
                except KeyError:
                    return Settings.show_error(
                        "Asset not found", "Enter a valid asset index"
                    )
                context.assets.append(asset)

    def ask(self, query, **kwargs):
        Settings.pieces_client.copilot.ask_stream_ws.on_message_callback = (
            self.on_message
        )
        Settings.get_model()  # Ensure the model is loaded
        if kwargs.get("ltm", False) and not enable_ltm():
            return
        files = kwargs.get("files", None)
        assets_index = kwargs.get("materials", None)
        self.add_context(files, assets_index)
        if not query:
            query = Settings.logger.input("prompt: ")
        if not query:
            Settings.logger.print("No query provided.")
            return

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
