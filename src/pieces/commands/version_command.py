from pieces.settings import Settings
from pieces import __version__
from pieces.gui import print_version_details


def version(**kwargs):
    if Settings.pieces_os_version:
        print_version_details(Settings.pieces_os_version, __version__)
    else:
        pass
