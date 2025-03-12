from rich.markdown import Markdown
from rich.console import Console
from ..settings import Settings


def feedback(**kwargs):
    console = Console()

    console.print(
        Markdown("Thank you for using Pieces CLI!\n"
                 "We always care about your feedback.\n"
                 "Feel free to share your experience with us.\n"
                 "https://github.com/pieces-app/cli-agent/discussions/194")
    )
    res = input(
        "Would you like to open the feedback page in your browser? (y/n): ")

    if res.lower() == 'y':
        Settings.open_website(
            "https://github.com/pieces-app/cli-agent/discussions/194")


def contribute(**kwargs):
    console = Console()

    console.print(
        "Contribute to the project\n"
        "https://github.com/pieces-app/cli-agent"
    )
    res = input(
        "Would you like to open the GitHub page in your browser? (y/n): ")

    if res.lower() == 'y':
        Settings.open_website("https://github.com/pieces-app/cli-agent")
