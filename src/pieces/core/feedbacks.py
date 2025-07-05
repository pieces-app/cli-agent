from pieces.urls import URLs
from pieces.settings import Settings


def feedback(**kwargs):
    """
    Redirects to github discussion to give feedback
    """
    Settings.logger.print(
        (
            "Thank you for using Pieces CLI!\n"
            "We always care about your feedback.\n"
            "Feel free to share your experience with us."
        )
    )
    link = URLs.PIECES_CLI_FEEDBACK_DISCUSSION
    Settings.logger.print(link.value)
    res = Settings.logger.confirm(
        "Would you like to open the feedback page in your browser?"
    )

    if res:
        link.open()


def contribute(**kwargs):
    """
    Redirects to github repo to contribute to the project
    """
    link = URLs.PIECES_CLI_REPO
    Settings.logger.print("Contribute to the project")
    Settings.logger.print(link.value)
    res = Settings.logger.confirm(
        "Would you like to open the GitHub page in your browser?"
    )

    if res:
        link.open()
