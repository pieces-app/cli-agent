"""
PiecesOS Update Module

This module provides functionality to update PiecesOS with progress display,
mirroring the behavior of the TypeScript modal but for CLI usage.
"""

import time
from typing import Optional
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    SpinnerColumn,
    TimeElapsedColumn,
)

from pieces.settings import Settings
from pieces._vendor.pieces_os_client.models.updating_status_enum import (
    UpdatingStatusEnum,
)
from pieces._vendor.pieces_os_client.models.unchecked_os_server_update import (
    UncheckedOSServerUpdate,
)
from pieces._vendor.pieces_os_client.exceptions import ApiException

# Constants
UPDATE_POLL_INTERVAL = 3  # seconds
UPDATE_TIMEOUT = 10 * 60  # 10 minutes
RECONNECT_POLL_INTERVAL = 0.5  # seconds
RECONNECT_TIMEOUT = 5 * 60  # 5 minutes


class PiecesUpdater:
    """
    Handles PiecesOS update process with progress display.

    This class manages the complete update workflow:
    1. Check for updates
    2. Download updates
    3. Restart PiecesOS
    4. Reconnect to updated instance
    """

    lock = False

    def __init__(self):
        self.cancel_requested = False

    def run(self) -> bool:
        """
        Execute the update process with separate widgets for each stage.

        Returns:
            bool: True if update successful, False otherwise
        """
        if self.lock:
            Settings.logger.print("❌ Update already in progress")
            return False

        self.lock = True

        try:
            status = self._check_for_updates_widget()
            if not status:
                return False

            if status == UpdatingStatusEnum.UP_TO_DATE:
                return True

            if not self._download_updates_widget():
                return False

            if not self._restart_widget():
                return False

            Settings.logger.print("✅ PiecesOS updated successfully!")
            return True

        except KeyboardInterrupt:
            self.cancel_requested = True
            Settings.logger.print("🚫 Update cancelled")
            return False
        finally:
            self.lock = False

    def _check_for_updates_widget(self) -> Optional[UpdatingStatusEnum]:
        """Widget 1: Check for updates with spinner"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=Settings.logger.console,
            transient=False,
        ) as progress:
            check_task = progress.add_task(
                "[cyan]Checking for updates...",
            )

            try:
                response = Settings.pieces_client.os_api.os_update_check(
                    unchecked_os_server_update=UncheckedOSServerUpdate()
                )

                if response.status == UpdatingStatusEnum.UP_TO_DATE:
                    progress.update(
                        check_task,
                        description="[green]PiecesOS is up to date",
                        completed=True,
                    )
                elif response.status in [
                    UpdatingStatusEnum.AVAILABLE,
                    UpdatingStatusEnum.DOWNLOADING,
                ]:
                    progress.update(
                        check_task,
                        description="[green]Update available!",
                        completed=True,
                    )
                else:
                    progress.update(
                        check_task,
                        description="[red]Update check failed",
                        completed=True,
                    )

                return response.status

            except Exception as e:
                progress.update(
                    check_task,
                    description=f"[red]Failed to check for updates: {e}",
                    completed=True,
                )
                Settings.logger.error(f"Failed to check for updates: {e}")
                return None

    def _download_updates_widget(self) -> bool:
        """Widget 2: Download updates with progress bar"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=Settings.logger.console,
            transient=False,
        ) as progress:
            download_task = progress.add_task(
                "Starting download...",
                total=100,
            )

            elapsed_time = 0

            while elapsed_time < UPDATE_TIMEOUT and not self.cancel_requested:
                try:
                    response = Settings.pieces_client.os_api.os_update_check(
                        unchecked_os_server_update=UncheckedOSServerUpdate()
                    )

                    # Use actual percentage from API if available, otherwise use 0
                    progress_percent = (
                        int(response.percentage)
                        if response.percentage is not None
                        else 0
                    )

                    if response.status == UpdatingStatusEnum.DOWNLOADING:
                        progress.update(
                            download_task,
                            description="Downloading update...",
                            completed=progress_percent,
                        )
                    elif response.status == UpdatingStatusEnum.READY_TO_RESTART:
                        progress.update(
                            download_task,
                            description="[green]Download completed!",
                            completed=100,
                        )
                        return True
                    elif response.status == UpdatingStatusEnum.UP_TO_DATE:
                        progress.update(
                            download_task,
                            description="[green]PiecesOS is up to date",
                            completed=100,
                        )
                        return True
                    elif response.status in [
                        UpdatingStatusEnum.CONTACT_SUPPORT,
                        UpdatingStatusEnum.REINSTALL_REQUIRED,
                    ]:
                        error_msg = self.get_status_message(response.status)
                        progress.update(
                            download_task,
                            description=f"[red]{error_msg}",
                            completed=100,
                        )
                        return False

                    time.sleep(UPDATE_POLL_INTERVAL)
                    elapsed_time += UPDATE_POLL_INTERVAL

                except ApiException as e:
                    if "connection" in str(e).lower():
                        time.sleep(UPDATE_POLL_INTERVAL)
                        elapsed_time += UPDATE_POLL_INTERVAL
                        continue
                    else:
                        progress.update(
                            download_task,
                            description=f"[red]API error: {e}",
                            completed=100,
                        )
                        return False

            progress.update(
                download_task,
                description="[red]Download timed out",
                completed=100,
            )
            return False

    def _restart_widget(self) -> bool:
        """Widget 3: Restart PiecesOS with spinner"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=Settings.logger.console,
            transient=False,
        ) as progress:
            restart_task = progress.add_task(
                "[cyan]Restarting PiecesOS...",
            )

            try:
                Settings.pieces_client.os_api.os_restart()
                time.sleep(4)

                progress.update(
                    restart_task,
                    description="[cyan]Opening PiecesOS...",
                )

                result = Settings.pieces_client.open_pieces_os()

                if result:
                    progress.update(
                        restart_task,
                        description="[green]PiecesOS restarted successfully!",
                        completed=True,
                    )
                    return True
                else:
                    progress.update(
                        restart_task,
                        description="[red]Failed to reconnect to PiecesOS",
                        completed=True,
                    )
                    return False

            except Exception as e:
                progress.update(
                    restart_task,
                    description=f"[red]Failed to restart PiecesOS: {e}",
                    completed=True,
                )
                Settings.logger.error(f"Failed to restart PiecesOS: {e}")
                return False

    def _poll_for_connection(self) -> bool:
        """Poll for PiecesOS connection after restart"""
        elapsed_time = 0

        while elapsed_time < RECONNECT_TIMEOUT and not self.cancel_requested:
            try:
                if Settings.pieces_client.is_pieces_running():
                    return True

                time.sleep(RECONNECT_POLL_INTERVAL)
                elapsed_time += RECONNECT_POLL_INTERVAL

            except Exception:
                # Expected during restart
                time.sleep(RECONNECT_POLL_INTERVAL)
                elapsed_time += RECONNECT_POLL_INTERVAL
                continue

        return False

    @staticmethod
    def get_status_message(status: UpdatingStatusEnum) -> str:
        """Get human-readable message for update status"""
        status_messages = {
            UpdatingStatusEnum.AVAILABLE: "Update available",
            UpdatingStatusEnum.DOWNLOADING: "Downloading update...",
            UpdatingStatusEnum.READY_TO_RESTART: "Ready to restart",
            UpdatingStatusEnum.UP_TO_DATE: "PiecesOS is up to date",
            UpdatingStatusEnum.REINSTALL_REQUIRED: "Reinstall required - please reinstall PiecesOS",
            UpdatingStatusEnum.CONTACT_SUPPORT: "Error occurred - contact support at https://docs.pieces.app/products/support",
            UpdatingStatusEnum.UNKNOWN: "Unknown",
        }
        return status_messages.get(status, "Unknown update status")


def update_pieces_os() -> bool:
    """
    Update PiecesOS with progress display.

    This function provides a simple interface to update PiecesOS,
    displaying progress with separate widgets for each stage.

    Returns:
        bool: True if update successful, False otherwise
    """
    updater = PiecesUpdater()
    Settings.startup()  # Ensure that POS is running
    return updater.run()
