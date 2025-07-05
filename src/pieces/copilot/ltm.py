import os
import threading
from typing import TYPE_CHECKING
from rich.progress import Progress, TextColumn
from rich.progress import SpinnerColumn
import time
import urllib3

from prompt_toolkit.formatted_text import HTML
from pieces.settings import Settings
from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.workstream_pattern_engine_vision_calibration import (
        WorkstreamPatternEngineVisionCalibration,
    )


class ConditionalSpinnerColumn(SpinnerColumn):
    def render(self, task):
        if task.completed:
            return ""
        return super().render(task)


QR_CODE_ASCII = """
████████████
██  ██    ██
████  ██  ██
██████    ██
██████  ████
████████████
"""


def get_padding(columns_count: int) -> str:
    return style_content((" " * columns_count), bg="white", fg="black")


def style_content(content: str, bg="default", fg="white") -> str:
    return f"<style bg='{bg}' fg='{fg}'>" + content + "</style>"


QR_PADDING = 2
LINE_OFFSET = 2


def add_qrcodes() -> "WorkstreamPatternEngineVisionCalibration":
    qr_lines = QR_CODE_ASCII.strip().split("\n")

    terminal_size = os.get_terminal_size()
    terminal_width = terminal_size.columns
    terminal_height = terminal_size.lines

    qr_num_lines = len(qr_lines)
    qr_num_columns = len(qr_lines[0])

    output_lines = [""] * terminal_height

    output_lines[0] = get_padding(qr_num_columns + QR_PADDING)
    for i, line in enumerate(qr_lines):
        output_lines[i + 1] = (
            get_padding(1)
            + line.replace("█", style_content(" ", "black"))
            + get_padding(1)
        )
    output_lines[qr_num_lines + 1] = get_padding(qr_num_columns + QR_PADDING)

    start_line = terminal_height - qr_num_lines
    if start_line < qr_num_lines:
        start_line = qr_num_lines

    spaces = " " * (terminal_width - 2 * qr_num_columns - 4)
    if qr_num_lines + 1 != start_line - LINE_OFFSET:
        output_lines[start_line - LINE_OFFSET] = " " * (qr_num_lines + QR_PADDING)

    output_lines[start_line - LINE_OFFSET] += style_content(spaces) + " " * (
        qr_num_columns + QR_PADDING
    )

    for i, line in enumerate(qr_lines):
        spaces = style_content(" " * (terminal_width - qr_num_columns - 2)) + " "
        output_lines[start_line + i - 1] = (
            spaces + line.replace("█", style_content(" ", "black")) + " "
        )
    output_lines[-1] = (
        style_content(" " * (terminal_width - qr_num_columns - 2))
        + (qr_num_columns + 2) * " "
    )

    window = Window(
        content=FormattedTextControl(
            HTML("\n".join(output_lines)), style="bg:white black"
        )
    )

    layout = Layout(container=window)

    application = Application(
        layout=layout,
        full_screen=True,
    )

    threading.Thread(target=lambda: capture(application)).start()

    return application.run()


def capture(application):
    s = Settings.pieces_client.copilot.context.ltm.capture()
    application.exit(result=s if s.dimensions else None)


def check_ltm(docs=None) -> bool:
    # Update the local cache
    Settings.pieces_client.copilot.context.ltm.ltm_status = Settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status()
    if Settings.pieces_client.copilot.context.ltm.is_enabled:
        return True

    if not Settings.logger.confirm(
        "Pieces LTM must be running, do you want to enable it?",
    ):
        return False
    missing_permissions = Settings.pieces_client.copilot.context.ltm.check_perms()
    if not missing_permissions:
        _open_ltm()
        return True

    with Progress(
        ConditionalSpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=Settings.logger.console,
        transient=False,
    ) as progress:
        if docs:
            Settings.logger.print(docs)
        vision_task = progress.add_task(
            "[cyan]Vision permission: checking...",
        )
        accessibility_task = progress.add_task(
            "[cyan]Accessibility permission: checking...",
        )
        main_task = progress.add_task(
            "[cyan]Checking PiecesOS permissions...", total=None
        )
        permissions_len = 100

        while True:
            try:
                missing_permissions = (
                    Settings.pieces_client.copilot.context.ltm.check_perms()
                )
                if len(missing_permissions) < permissions_len:
                    # at least there is a progress here let's show the message again
                    show_message = True
                else:
                    show_message = False

                permissions_len = len(missing_permissions)
                if "vision" not in missing_permissions:
                    progress.update(
                        vision_task,
                        description="[green]Vision permission: enabled",
                        completed=True,
                    )
                else:
                    progress.update(
                        vision_task,
                        description="[yellow]Vision permission: enabling...",
                    )
                if "accessibility" not in missing_permissions:
                    progress.update(
                        accessibility_task,
                        description="[green]Accessibility permission: enabled",
                        completed=True,
                    )
                else:
                    progress.update(
                        accessibility_task,
                        description="[yellow]Accessibility permission: enabling...",
                    )

                if not missing_permissions:
                    progress.update(
                        main_task,
                        description="[green]All permissions are activated",
                        completed=True,
                    )
                    break

                progress.update(
                    main_task,
                    description=f"[yellow]Found {permissions_len} missing permissions",
                )

                if show_message:
                    Settings.pieces_client.copilot.context.ltm.enable(True)
                else:
                    time.sleep(3)  # 3 sec delay
            except PermissionError:
                pass
            except (
                urllib3.exceptions.ProtocolError,
                urllib3.exceptions.NewConnectionError,
                urllib3.exceptions.ConnectionError,
                urllib3.exceptions.MaxRetryError,
            ):  # Hope we did not forgot any exception
                progress.update(
                    main_task,
                    description="[yellow]PiecesOS is restarting...",
                )

                progress.update(vision_task, visible=False)
                progress.update(accessibility_task, visible=False)

                if Settings.pieces_client.is_pieces_running(maximum_retries=10):
                    missing_permissions = (
                        Settings.pieces_client.copilot.context.ltm.check_perms()
                    )
                    if not missing_permissions:
                        progress.update(
                            main_task,
                            description="[green]All permissions are enabled!",
                            completed=True,
                        )
                        time.sleep(0.5)
                        break
                    else:
                        progress.update(vision_task, visible=True)
                        progress.update(accessibility_task, visible=True)
                else:
                    progress.update(
                        main_task,
                        description="[red]Failed to open PiecesOS",
                        completed=True,
                    )
                    time.sleep(1)
                    return False
            except KeyboardInterrupt:
                progress.update(vision_task, visible=False)
                progress.update(accessibility_task, visible=False)

                progress.update(
                    main_task,
                    description="[red]Operation cancelled by user",
                    completed=True,
                )
                return False
            except Exception as e:
                progress.update(vision_task, visible=False)
                progress.update(accessibility_task, visible=False)

                progress.update(
                    main_task,
                    description=f"[red]Unexpected error: {str(e)}",
                    completed=True,
                )
                return False
        _open_ltm()

        return True


def _open_ltm():
    try:
        Settings.pieces_client.copilot.context.ltm.enable(
            False
        )  # Don't show any permission notification/pop up
    except Exception as e:
        Settings.show_error(f"Error in enabling the LTM: {e}")


def enable_ltm():
    if check_ltm():
        # window = add_qrcodes()  # TODO: Clean at exist
        # if not window:
        #     Settings.show_error(
        #         "Couldn't enable ltm for this chat",
        #         f"Please use another terminal and report this issue\n{URLs.PIECES_CLI_ISSUES.value}",
        #     )
        #     return False
        Settings.pieces_client.copilot.context.ltm.chat_enable_ltm()
        return True
    return False
