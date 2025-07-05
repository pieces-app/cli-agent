import sys
import subprocess
from enum import Enum
from tempfile import gettempdir
import re
import threading
import time
from typing import List, Optional, Tuple, Callable

import urllib.request


class PlatformEnum(Enum):
    Windows = 'Windows'
    Linux = 'Linux'
    Macos = 'Macos'


class DownloadState(Enum):
    IDLE = 'IDLE'
    DOWNLOADING = 'DOWNLOADING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class TerminalEventType(Enum):
    PROMPT = 'PROMPT'
    OUTPUT = 'OUTPUT'
    ERROR = 'ERROR'


class DownloadModel:
    def __init__(self, state: DownloadState, terminal_event: TerminalEventType,
                 bytes_received: int = 0, total_bytes: int = 0,
                 percent: float = 0):
        self.bytes_received = bytes_received
        self.total_bytes = total_bytes
        self.percent = percent
        self.state = state
        self.terminal_event = terminal_event


class PosInstaller:
    def __init__(self, callback: Optional[Callable[[DownloadModel], None]],
                 product: str):
        self.platform = self.detect_platform()
        self.download_process = None
        self.progress_update_callback = callback
        self.state = DownloadState.IDLE
        self.terminal_event = TerminalEventType.PROMPT
        self.stop = False
        self.thread = None
        self.product = product

    def update_progress(self, bytes_received: int = 0, total_bytes: int = 0):
        if self.progress_update_callback:
            if total_bytes == 0:
                percent = 0
            else:
                percent = (bytes_received/total_bytes)*100
            progress = DownloadModel(
                self.state, self.terminal_event,
                bytes_received, total_bytes, percent)
            self.progress_update_callback(progress)

    @staticmethod
    def detect_platform() -> PlatformEnum:
        if sys.platform == 'win32':
            return PlatformEnum.Windows
        elif sys.platform == 'linux':
            return PlatformEnum.Linux
        else:
            return PlatformEnum.Macos

    def start_download(self) -> bool:
        if self.state == DownloadState.DOWNLOADING:
            return False

        self.state = DownloadState.DOWNLOADING
        self.update_progress()
        self.thread = threading.Thread(
            target=self._start_download, daemon=True)
        self.thread.start()
        return True

    def _start_download(self):
        try:
            if self.platform == PlatformEnum.Windows:
                self.download_windows()
            elif self.platform == PlatformEnum.Linux:
                self.download_linux()
            elif self.platform == PlatformEnum.Macos:
                self.download_macos()
        except Exception as e:
            print(f"Error: {e}")
            self.state = DownloadState.FAILED
            self.update_progress()

    def download_linux(self):
        self.print('Starting POS download for Linux.')
        command = '''
            if command -v pkexec >/dev/null 2>&1; then
              pkexec snap install pieces-os && \
              pkexec snap connect pieces-os:process-control :process-control && \
              pieces-os
            else
              echo "Error: pkexec is not available. Exiting." >&2
              exit 1
            fi
        '''
        self.execute_command('bash', '-c', [command], self.extract_linux_regex)

    def download_macos(self):
        self.print('Starting POS download for Macos.')

        arch = 'arm64' if sys.maxsize > 2**32 else 'x86_64'
        pkg_url = (f'https://builds.pieces.app/stages/production/'
                   f'macos_packaging/pkg-pos-launch-only-{arch}/'
                   f'download?product={self.product}&download=true')
        tmp_pkg_path = "/tmp/Pieces-OS-Launch.pkg"
        self.install_using_web(pkg_url, tmp_pkg_path)

    def download_windows(self):
        self.print('Starting POS download for Windows.')
        pkg_url = ('https://builds.pieces.app/stages/production/os_server/windows-exe'
                   f"/download?download=true&product={self.product}")
        tmp_pkg_path = f"{gettempdir()}\\Pieces-OS.exe"
        self.install_using_web(pkg_url, tmp_pkg_path)

    def install_using_web(self, pkg_url: str, tmp_pkg_path: str) -> bool:
        BUFFER_SIZE = 65536
        STALL_TIMEOUT = 5
        try:
            self.state = DownloadState.DOWNLOADING
            request = urllib.request.Request(
                pkg_url, headers={'Accept': '*/*'})
            response = urllib.request.urlopen(request)
            file_size = int(response.info().get('Content-Length', 0))
            downloaded_size = 0

            with open(tmp_pkg_path, 'wb') as out_file:
                last_data_time = time.time()
                while True:
                    data = response.read(BUFFER_SIZE)
                    if not data:
                        break
                    if self.stop:
                        self.print("Download stopped by user.")
                        self.update_progress_stop()
                        return False

                    out_file.write(data)
                    downloaded_size += len(data)
                    last_data_time = time.time()

                    if downloaded_size % (512 * 1024) == 0 or downloaded_size == file_size:
                        self.update_progress(downloaded_size, file_size)
                        self.print(
                            f'Downloaded {downloaded_size} of {file_size}')
                    if time.time() - last_data_time > STALL_TIMEOUT:
                        raise TimeoutError(
                            "Download stalled (no data received).")

                    self.update_progress(downloaded_size, file_size)
                    self.print(f'Downloaded {downloaded_size} of {file_size}')

            self.state = DownloadState.COMPLETED
            self.update_progress()
            self.print(f'Download completed. Opening {tmp_pkg_path}.')
            if sys.platform == 'win32':
                subprocess.run(['start', tmp_pkg_path], shell=True)
            else:
                subprocess.run(['open', tmp_pkg_path])
            return True
        except Exception as e:
            self.state = DownloadState.FAILED
            self.update_progress()
            self.print(f'Error downloading POS: {e}')
            return False

    def extract_linux_regex(self, line) -> Optional[Tuple[int, int]]:
        pattern = r"(\d+)%\s+([\d.]+)MB/s\s+([\dms.]+)"

        match = re.search(pattern, line)

        if match:
            percentage = match.group(1)
            download_speed = match.group(2)
            time_remaining = match.group(3)
            total_bytes = int(download_speed) * int(time_remaining)
            bytes_downloaded = (int(percentage) / 100) * total_bytes

            return bytes_downloaded, total_bytes

    def execute_command(self, shell: str, command: str, args: List[str],
                        callback: Optional[Callable[[str], Tuple[int, int]]]
                        ) -> bool:
        try:
            self.print(f'Spawning process: {shell} {command} {args}')
            self.download_process = subprocess.Popen(
                [shell, command] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            while True:
                out = self.download_process.stdout
                err = self.download_process.stderr

                if out:
                    self.state = DownloadState.DOWNLOADING
                    self.terminal_event = TerminalEventType.OUTPUT
                    try:
                        bytes_received, total_bytes = callback(
                            out.readline().decode('utf-8'))
                        self.print(
                            f'Downloaded {bytes_received} of {total_bytes}')
                        self.update_progress(bytes_received, total_bytes)
                    except Exception as e:
                        self.print(
                            f"Could not match pattern: {e}", file=sys.stderr)

                if err:
                    self.terminal_event = TerminalEventType.ERROR
                    self.update_progress(bytes_received=0, total_bytes=0)
                    self.print(err.readline().decode('utf-8'), file=sys.stderr)

                if self.download_process.poll() is not None:
                    break

            self.download_process.wait()
            self.print('Process completed.')
            return self.download_process.returncode == 0
        except Exception as e:
            self.print(f'Error executing command: {e}')
            self.state = DownloadState.FAILED
            self.update_progress()
            return False

    def cancel_download(self) -> None:
        if self.state == DownloadState.DOWNLOADING:
            if self.download_process:
                self.download_process.kill()
                self.update_progress_stop()
            else:
                self.stop = True

    def update_progress_stop(self) -> None:
        self.state = DownloadState.IDLE
        self.terminal_event = TerminalEventType.OUTPUT
        self.update_progress()
        self.print('Download canceled.')

    def print(self, message, file=sys.stdout):  # for debugging
        return
        # print(message, file=file)
