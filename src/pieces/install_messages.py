"""User-facing PiecesOS install messages.

Mirrors ``src/pieces/readiness_messages.py``: stdlib-only, zero ``pieces.*``
imports, pure functions returning strings so the wording is testable without
running the installer.

Wording constraints (do not relax without re-review):

- Do not overclaim install state. On macOS/Windows the installer only
  downloads the package and launches the OS installer; the user must still
  finish the GUI install. Only Linux (snap) actually installs in-process.
- These helpers select wording only. They must not change install behavior
  or control flow.
"""


def install_completed_message(system: str) -> str:
    """Return the success message for a finished download/install.

    ``system`` is the value of ``platform.system()`` ("Linux", "Darwin",
    "Windows"). Only Linux performs an in-process install (snap); macOS and
    Windows merely download the package and open the OS installer, so they get
    download-oriented wording that points the user at the launched installer.
    """
    if system == "Linux":
        return "✅ Installed PiecesOS. Run `pieces open` to launch it."
    return "📥 Downloaded PiecesOS. Finish the installation in the window that just opened, then run `pieces open`."


def install_failed_message() -> str:
    """Return the failure message shown before opening the manual install page."""
    return "❌ Couldn't install PiecesOS automatically — opening the manual install page in your browser."
