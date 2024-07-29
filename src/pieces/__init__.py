import importlib.metadata

try:
    __version__ = importlib.metadata.version("pieces-cli")
except importlib.metadata.PackageNotFoundError:
    print("Could not find the 'pieces-cli' package in the Python environment. Is it installed?")
    __version__ = "unknown"

