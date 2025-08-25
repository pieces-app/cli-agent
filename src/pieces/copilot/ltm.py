"""
Long Term Memory (LTM) management module for Pieces CLI.

This module handles the setup, configuration, and enabling of LTM functionality,
including permission management and progress reporting through different interfaces.
"""

import os
import threading
import time
import urllib3
from typing import TYPE_CHECKING, Optional

from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from rich.progress import SpinnerColumn

from pieces.headless.exceptions import HeadlessLTMNotEnabledError
from pieces.settings import Settings

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.workstream_pattern_engine_vision_calibration import (
        WorkstreamPatternEngineVisionCalibration,
    )


class ConditionalSpinnerColumn(SpinnerColumn):
    """A spinner column that hides the spinner when the task is completed.

    This custom spinner column extends Rich's SpinnerColumn to provide
    conditional rendering - the spinner is only shown for active tasks
    and disappears once the task is marked as completed.
    """

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

    window: Window = Window(
        content=FormattedTextControl(
            HTML("\n".join(output_lines)), style="bg:white black"
        )
    )

    layout: Layout = Layout(container=window)

    application: Application = Application(
        layout=layout,
        full_screen=True,
    )

    threading.Thread(target=lambda: capture(application)).start()

    return application.run()


def capture(application: Application) -> None:
    """
    Capture LTM calibration data and exit the application.

    Args:
        application: The prompt-toolkit Application instance
    """
    s = Settings.pieces_client.copilot.context.ltm.capture()
    application.exit(result=s if s.dimensions else None)


def update_ltm_cache() -> None:
    """
    Update the local LTM status cache from the workstream pattern engine.

    This function refreshes the cached LTM status by querying the current
    vision status from the workstream pattern engine API.
    """
    Settings.pieces_client.copilot.context.ltm.ltm_status = Settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status()


class LTMEnabler:
    """Object-oriented enabler for Long Term Memory (LTM).

    Encapsulates the state and behavior required to check permissions and
    enable LTM using either CLI Rich progress or a provided TUI dialog.
    """

    def __init__(
        self,
        docs: Optional[str] = None,
        auto_enable: bool = False,
        tui_dialog=None,
    ) -> None:
        self.docs = docs
        self.auto_enable = auto_enable
        self.tui_dialog = tui_dialog

        self.is_tui = bool(tui_dialog)
        self.vision_task = None
        self.accessibility_task = None
        self.main_task = None

    def start_progress(self):
        if self.tui_dialog:
            self.rich_progress = self.tui_dialog.rich_progress
            self.vision_task = self.tui_dialog._vision_task
            self.accessibility_task = self.tui_dialog._accessibility_task
            self.main_task = self.tui_dialog._main_task

            def refresh_display():
                def update():
                    if self.tui_dialog:
                        self.tui_dialog._refresh_display()

                if self.tui_dialog:
                    self.tui_dialog.call_from_thread(update)

            self._refresh_display = refresh_display
        else:
            from rich.progress import Progress, TextColumn

            self.rich_progress = Progress(
                ConditionalSpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=Settings.logger.console,
                transient=False,
            )

            if self.docs:
                Settings.logger.print(self.docs)
            self.rich_progress.start()

            # Create tasks for CLI mode
            self.vision_task = self.rich_progress.add_task(
                "[cyan]Vision permission: checking..."
            )
            self.accessibility_task = self.rich_progress.add_task(
                "[cyan]Accessibility permission: checking..."
            )
            self.main_task = self.rich_progress.add_task(
                "[cyan]Checking PiecesOS permissions...", total=None
            )

            def refresh_display():
                pass

            self._refresh_display = refresh_display

    def update_main_status(self, message: str, completed: bool = False) -> None:
        if self.main_task is not None:
            self.rich_progress.update(
                self.main_task, description=message, completed=completed
            )
            self._refresh_display()

    def hide_permission_tasks(self) -> None:
        if self.vision_task is not None:
            self.rich_progress.update(self.vision_task, visible=False)
        if self.accessibility_task is not None:
            self.rich_progress.update(self.accessibility_task, visible=False)
        self._refresh_display()

    def show_permission_tasks(self) -> None:
        if self.vision_task is not None:
            self.rich_progress.update(self.vision_task, visible=True)
        if self.accessibility_task is not None:
            self.rich_progress.update(self.accessibility_task, visible=True)
        self._refresh_display()

    def update_permission_status(self, missing_permissions) -> None:
        # Vision
        if self.vision_task is not None:
            if "vision" not in missing_permissions:
                self.rich_progress.update(
                    self.vision_task,
                    description="[green]Vision permission: enabled",
                    completed=True,
                )
            else:
                self.rich_progress.update(
                    self.vision_task,
                    description="[yellow]Vision permission: enabling...",
                )

        # Accessibility
        if self.accessibility_task is not None:
            if "accessibility" not in missing_permissions:
                self.rich_progress.update(
                    self.accessibility_task,
                    description="[green]Accessibility permission: enabled",
                    completed=True,
                )
            else:
                self.rich_progress.update(
                    self.accessibility_task,
                    description="[yellow]Accessibility permission: enabling...",
                )

        self._refresh_display()

    def _stop_progress(self) -> None:
        try:
            if hasattr(self, "rich_progress") and self.rich_progress:
                if self.main_task:
                    self.rich_progress.remove_task(self.main_task)
                self.hide_permission_tasks()
                self.rich_progress.stop()
        except Exception:
            pass

    def run(self) -> bool:
        Settings.pieces_client.copilot.context.ltm.ltm_status = Settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status()

        if Settings.pieces_client.copilot.context.ltm.is_enabled:
            self._stop_progress()
            return True

        if Settings.headless_mode:
            self._stop_progress()
            raise HeadlessLTMNotEnabledError()

        if not self.auto_enable and not Settings.logger.confirm(
            "Pieces LTM must be running, do you want to enable it?",
        ):
            self._stop_progress()
            return False

        self.start_progress()
        missing_permissions = Settings.pieces_client.copilot.context.ltm.check_perms()
        if not missing_permissions:
            _open_ltm()
            self._stop_progress()
            return True

        try:
            permissions_len = 100

            while True:
                try:
                    missing_permissions = (
                        Settings.pieces_client.copilot.context.ltm.check_perms()
                    )

                    if len(missing_permissions) < permissions_len:
                        show_message = True
                    else:
                        show_message = False

                    permissions_len = len(missing_permissions)

                    self.update_permission_status(missing_permissions)

                    if not missing_permissions:
                        self.update_main_status(
                            "[green]All permissions are activated", completed=True
                        )
                        break

                    self.update_main_status(
                        f"[yellow]Found {permissions_len} missing permissions"
                    )

                    if show_message:
                        Settings.pieces_client.copilot.context.ltm.enable(True)
                    else:
                        time.sleep(3)

                except PermissionError:
                    pass
                except (
                    urllib3.exceptions.ProtocolError,
                    urllib3.exceptions.NewConnectionError,
                    urllib3.exceptions.ConnectionError,
                    urllib3.exceptions.MaxRetryError,
                ):
                    self.update_main_status("[yellow]PiecesOS is restarting...")
                    self.hide_permission_tasks()

                    if Settings.pieces_client.is_pieces_running(maximum_retries=10):
                        missing_permissions = (
                            Settings.pieces_client.copilot.context.ltm.check_perms()
                        )
                        if not missing_permissions:
                            self.update_main_status(
                                "[green]All permissions are enabled!", completed=True
                            )
                            time.sleep(0.5)
                            break
                        else:
                            self.show_permission_tasks()
                    else:
                        self.update_main_status(
                            "[red]Failed to open PiecesOS", completed=True
                        )
                        if self.tui_dialog:
                            self.tui_dialog.set_complete(
                                False, "❌ Failed to open PiecesOS"
                            )
                        time.sleep(1)
                        return False
                except KeyboardInterrupt:
                    self.hide_permission_tasks()
                    self.update_main_status(
                        "[red]Operation cancelled by user", completed=True
                    )
                    if self.tui_dialog:
                        self.tui_dialog.set_complete(
                            False, "❌ Operation cancelled by user"
                        )
                    return False
                except Exception as e:
                    self.hide_permission_tasks()
                    self.update_main_status(
                        f"[red]Unexpected error: {str(e)}", completed=True
                    )
                    if self.tui_dialog:
                        self.tui_dialog.set_complete(
                            False, f"❌ Unexpected error: {str(e)}"
                        )
                    return False

            _open_ltm()
            if self.tui_dialog:
                self.tui_dialog.set_complete(True, "✅ LTM successfully enabled!")
            else:
                self.update_main_status(
                    "[green]✅ LTM successfully enabled!", completed=True
                )
                time.sleep(0.5)
            return True
        finally:
            self._stop_progress()


def check_ltm(
    docs: Optional[str] = None,
    auto_enable: bool = False,
    tui_dialog=None,
) -> bool:
    """Check and enable LTM via the LTMEnabler class."""
    return LTMEnabler(docs=docs, auto_enable=auto_enable, tui_dialog=tui_dialog).run()


def _open_ltm() -> None:
    """
    Open and enable LTM without showing permission notifications.

    This function enables the LTM system by calling the client's enable method
    with notifications disabled to avoid popup dialogs.

    Raises:
        Logs errors if enabling LTM fails
    """
    try:
        Settings.pieces_client.copilot.context.ltm.enable(
            False
        )  # Don't show any permission notification/pop up
    except Exception as e:
        Settings.show_error(f"Error in enabling the LTM: {e}")


def enable_ltm(auto_enable: bool = False) -> bool:
    """
    Enable Long Term Memory (LTM) for chat functionality.

    This function checks if LTM is available and enables it for chat usage.
    It first ensures system LTM is enabled, then enables chat-specific LTM.

    Args:
        auto_enable: Whether to automatically enable without user confirmation

    Returns:
        True if LTM was successfully enabled for chat, False otherwise

    Note:
        The QR code functionality is currently commented out but may be
        re-enabled in future versions for enhanced calibration.
    """
    if check_ltm(None, auto_enable):
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
