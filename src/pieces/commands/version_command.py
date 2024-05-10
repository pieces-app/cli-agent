from pieces.settings import Settings
from pieces import __version__

def version(**kwargs):
    if Settings.pieces_os_version:
        print(f"Pieces Version: {Settings.pieces_os_version}")
        print(f"Cli Version: {__version__}")
    else:
        pass