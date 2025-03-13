import os
import queue
from typing import Generator
from rich.progress import (Progress,
                           BarColumn,
                           DownloadColumn,
                           TransferSpeedColumn)
from ..wrapper.installation import (DownloadModel,
                                    DownloadState)
from ..settings import Settings


class PiecesInsertaller():
    lock = False

    def run(self):
        self.queue = queue.Queue()
        if self.lock:
            return
        self.lock = True
        self.installer = Settings.pieces_client.pieces_os_installer(
            self.queue.put)
        self.installer.start_download()
        m = self.queue.get()  # Block the thread until we recieve the first byte
        try:
            print("Installing PiecesOS")
            with Progress(
                BarColumn(),
                DownloadColumn(),
                TransferSpeedColumn(),
                auto_refresh=False,
                transient=True
            ) as progress:
                task = progress.add_task(
                    description="Installion PiecesOS",
                    total=m.total_bytes,
                )
                for model in self.iterator():
                    progress.update(task, total=model.total_bytes,
                                    completed=model.bytes_received)
                    if model.state == DownloadState.FAILED:
                        print(
                            "❌ Failed to install PiecesOS,"
                            " Opening in your webbrowser")
                        self.download_docs()
                    elif model.state == DownloadState.COMPLETED:
                        print("✅ Installed PiecesOS successfully")
                    progress.refresh()
        except KeyboardInterrupt:
            self.installer.cancel_download()
            print("🚫 Installation cancelled")
            self.lock - False

    def iterator(self) -> Generator[DownloadModel, None, None]:
        while True:
            m = self.queue.get()
            if m.state != DownloadState.DOWNLOADING:
                yield m
                self.lock = False
                break
            yield m

    def download_docs(self):
        if Settings.pieces_client.local_os == "WINDOWS":
            Settings.open_website(
                f"https://builds.pieces.app/stages/production/appinstaller/os_server.appinstaller?product=PIECES_FOR_DEVELOPERS_CLI&download=true")
        elif Settings.pieces_client.local_os == "LINUX":
            Settings.open_website("https://snapcraft.io/pieces-os")
            return

        elif Settings.pieces_client.local_os == "MACOS":
            arch = os.uname().machine
            pkg_url = (
                "https://builds.pieces.app/stages/production/macos_packaging/pkg-pos-launch-only"
                f"{'-arm64' if arch == 'arm64' else ''}"
                f"/download?product=PIECES_FOR_DEVELOPERS_CLI&download=true"
            )
            Settings.open_website(pkg_url)

        else:
            raise ValueError("Invalid platform")
