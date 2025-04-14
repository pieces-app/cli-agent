from ..settings import Settings
from pieces_os_client.models.inactive_os_server_applet import InactiveOSServerApplet
from pieces_os_client.models.os_applet_enum import OSAppletEnum


def open_command(**kwargs):
    copilot = kwargs.get("copilot")
    drive = kwargs.get("drive")

    # Let's try to Open POS
    health = Settings.pieces_client.open_pieces_os()

    if (drive or copilot) and not health:
        print("PiecesOS is not running")
        return

    if copilot:
        Settings.open_website(
            "localhost:"
            + str(
                Settings.pieces_client.os_api.os_applet_launch(
                    InactiveOSServerApplet(type=OSAppletEnum.COPILOT)
                ).port
            )
        )
    if drive:
        Settings.open_website(
            "localhost:"
            + str(
                Settings.pieces_client.os_api.os_applet_launch(
                    InactiveOSServerApplet(type=OSAppletEnum.SAVED_MATERIALS)
                ).port
            )
        )
