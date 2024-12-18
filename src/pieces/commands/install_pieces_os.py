import os

from pieces.settings import Settings

def install_pieces_os(**kwargs):
    """
    Install Pieces OS based on the platform
    """
    
    if Settings.pieces_client.local_os == "WINDOWS":
        install_command = (
            f'Add-AppxPackage -Appinstaller "https://builds.pieces.app/stages/production/appinstaller/os_server.appinstaller?product={Settings.pieces_client.app_name}&download=true"'
            '-ErrorAction Stop -Verbose ; '
            'Start-Process shell:appsFolder\\com.MeshIntelligentTechnologi.PiecesOS_84gz00a5z79wr!osserver'
        )
        os.system(install_command)
    
    elif Settings.pieces_client.local_os == "LINUX":
        install_command = (
            'sudo snap install pieces-os && '
            'sudo snap connect pieces-os:process-control :process-control && '
            'sudo snap install pieces-for-developers && '
            'pieces-os'
        )
        os.system(install_command)
        return
    
    elif Settings.pieces_client.local_os == "MACOS":
        arch = os.uname().machine
        pkg_url = (
            "https://builds.pieces.app/stages/production/macos_packaging/pkg-pos-launch-only"
            f"{'-arm64' if arch == 'arm64' else ''}/download?product={Settings.pieces_client.app_name}&download=true"
        )
        script = f"""
        TMP_PKG_PATH="/tmp/Pieces-OS-Launch.pkg"
        echo "Downloading Pieces OS .pkg file from {pkg_url}..."
        curl -L "{pkg_url}" -o "$TMP_PKG_PATH"
        if [ -f "$TMP_PKG_PATH" ]; then
            echo "Pieces OS Download successful, installing the package..."
            open "$TMP_PKG_PATH"
            echo "Pieces OS Installation complete."
        else
            echo "Failed to download and install Pieces OS."
        fi
        """
        os.system(script)
    
    else:
        print("Error: Unsupported platform.")
