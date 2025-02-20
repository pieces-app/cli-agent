import os
import subprocess
from pieces.settings import Settings

def install_pieces_os(**kwargs):
    """
    Install PiecesOS based on the platform
    """
    try:
        if Settings.pieces_client.local_os == "WINDOWS":
            install_command = [
                "powershell.exe",
                "Add-AppxPackage",
                "-Appinstaller",
                "https://builds.pieces.app/stages/production/appinstaller/os_server.appinstaller",
                "-ErrorAction",
                "Stop",
                "-Verbose"
            ]
            print("Installing PiecesOS... This might take a few minutes.")
            process = subprocess.Popen(install_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in process.stdout:
                print(line, end='')

            process.wait()
        
        elif Settings.pieces_client.local_os == "LINUX":
            install_command = (
                'sudo snap install pieces-os && '
                'sudo snap connect pieces-os:process-control :process-control && '
                'sudo snap install pieces-for-developers && '
                'pieces-os'
            )
            subprocess.Popen(install_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            return
        
        elif Settings.pieces_client.local_os == "MACOS":
            arch = os.uname().machine
            pkg_url = (
                "https://builds.pieces.app/stages/production/macos_packaging/pkg-pos-launch-only"
                f"{'-arm64' if arch == 'arm64' else ''}/download?product={Settings.pieces_client.app_name}&download=true"
            )
            script = f"""
            TMP_PKG_PATH="/tmp/Pieces-OS-Launch.pkg"
            echo "Downloading PiecesOS .pkg file from {pkg_url}..."
            curl -L "{pkg_url}" -o "$TMP_PKG_PATH"
            if [ -f "$TMP_PKG_PATH" ]; then
                echo "PiecesOS Download successful, installing the package..."
                open "$TMP_PKG_PATH"
                echo "PiecesOS Installation complete."
            else
                echo "Failed to download and install PiecesOS."
            fi
            """
            subprocess.run(["sh", "-c", script], check=True)
        
        else:
            print("Error: Unsupported platform.")
    except KeyboardInterrupt:
        print("Download interrupted by user.")

