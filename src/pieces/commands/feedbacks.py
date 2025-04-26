from rich.markdown import Markdown
from ..settings import Settings


def feedback(**kwargs):
    Settings.logger.print(
        (
            "Thank you for using Pieces CLI!\n"
            "We always care about your feedback.\n"
            "Feel free to share your experience with us."
        )
    )
    Settings.logger.print("https://github.com/pieces-app/cli-agent/discussions/194")
    res = Settings.logger.confirm(
        "Would you like to open the feedback page in your browser?"
    )

    if res:
        Settings.open_website("https://github.com/pieces-app/cli-agent/discussions/194")


def contribute(**kwargs):
    Settings.logger.print("Contribute to the project")
    Settings.logger.print("https://github.com/pieces-app/cli-agent")
    res = Settings.logger.confirm(
        "Would you like to open the GitHub page in your browser?"
    )

    if res:
        Settings.open_website("https://github.com/pieces-app/cli-agent")
