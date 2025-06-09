import queue
from typing import Generator
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn
from pieces._vendor.pieces_os_client.wrapper.installation import DownloadModel, DownloadState
from ..settings import Settings
from pieces.urls import URLs
import platform


class PiecesInstaller:
    lock = False

    def run(self):
        self.queue = queue.Queue()
        if self.lock:
            return
        self.lock = True
        self.installer = Settings.pieces_client.pieces_os_installer(self.queue.put)
        self.installer.start_download()
        m = self.queue.get()  # Block the thread until we recieve the first byte
        try:
            Settings.logger.print("Installing PiecesOS")
            with Progress(
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                auto_refresh=False,
                transient=True,
            ) as progress:
                task = progress.add_task(
                    description="Installation PiecesOS",
                    total=m.total_bytes,
                )
                for model in self.iterator():
                    progress.update(
                        task, total=model.total_bytes, completed=model.bytes_received
                    )
                    if model.state == DownloadState.FAILED:
                        Settings.logger.print(
                            "❌ Failed to install PiecesOS, Opening in your webbrowser"
                        )
                        self.download_docs()
                    elif model.state == DownloadState.COMPLETED:
                        Settings.logger.print("✅ Installed PiecesOS successfully")
                    progress.refresh()
        except KeyboardInterrupt:
            self.installer.cancel_download()
            Settings.logger.print("🚫 Installation cancelled")
            self.lock = False

    def iterator(self) -> Generator[DownloadModel, None, None]:
        while True:
            m = self.queue.get()
            if m.state != DownloadState.DOWNLOADING:
                yield m
                self.lock = False
                break
            yield m

    def download_docs(self):
        if platform.system() == "Windows":
            URLs.PIECES_OS_DOWNLOAD_WINDOWS.open()
        elif platform.system() == "Linux":
            URLs.PIECES_OS_DOWNLOAD_LINUX.open()
        elif platform.system() == "Darwin":
            if platform.machine() == "arm64":
                URLs.PIECES_OS_DOWNLOAD_MACOS_ARM64.open()
            else:
                URLs.PIECES_OS_DOWNLOAD_MACOS_X86.open()
        else:
            raise ValueError("Invalid platform")
