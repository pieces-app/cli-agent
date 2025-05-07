from ..settings import Settings
from pieces_os_client.models.inactive_os_server_applet import InactiveOSServerApplet
from pieces_os_client.models.os_applet_enum import OSAppletEnum


def open_command(**kwargs):
    copilot = kwargs.get("copilot", False)
    drive = kwargs.get("drive", False,)
    settings = kwargs.get("settings", False)

    # Let's try to Open POS
    health = Settings.pieces_client.open_pieces_os()

    if (drive or copilot or settings) and not health:
        Settings.logger.print("PiecesOS is not running")
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
    if settings:
        Settings.open_website(
            "localhost:"
            + str(
                Settings.pieces_client.os_api.os_applet_launch(
                    InactiveOSServerApplet(
                        type=OSAppletEnum.FUTURE_APPLET_MODULE_PLACEHOLDER_A)
                ).port
            )
        )
