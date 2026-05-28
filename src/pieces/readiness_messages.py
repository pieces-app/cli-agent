"""User-facing PiecesOS readiness messages.

Lives at top-level (NOT under ``pieces.core``) to avoid a circular import
through ``pieces.settings``. Every module under ``pieces.core`` imports
``Settings`` at module top, so ``pieces.settings -> pieces.core.<x>`` would
re-enter a partially-loaded ``pieces.settings`` and raise ``ImportError``.

Constraints (do not relax without re-review):

- stdlib-only imports. Do not import ``Settings``. Do not import anything
  under ``pieces.core``. Do not import ``pieces.urls`` (it is safe today
  but keeping zero ``pieces.*`` imports here removes the entire cycle
  surface).
- Do not claim install state. The CLI cannot tell "not installed" apart
  from "installed but not running" from ``open_pieces_os()`` alone.
- Do not mention ``.port.txt``. The CLI does not read it.
- Always end with the same four next steps: ``pieces install``,
  ``pieces open``, retry, share ``pieces version`` output with support.
- Long-form is multi-line Markdown for
  ``Settings.logger.print(Markdown(...))``.
- Short-form is a single-line Rich-markup string safe for
  ``Progress.update(..., description=...)``.
"""


def pieces_os_not_reachable() -> str:
    """Return the long-form canonical readiness message as Markdown.

    Intended to be wrapped in ``rich.markdown.Markdown`` before being
    handed to ``Settings.logger.print``.
    """
    return (
        "**PiecesOS is not reachable from the CLI.**\n\n"
        "**Possible reasons:**\n\n"
        "- PiecesOS may need to be installed or updated\n"
        "- PiecesOS may not be running\n"
        "- PiecesOS may still be starting up\n\n"
        "**Try:**\n\n"
        "1. Install or update PiecesOS: `pieces install`\n"
        "2. Launch PiecesOS: `pieces open`\n"
        "3. If you just installed it, wait a few seconds and retry your command\n"
        "4. If the problem persists, share the output of `pieces version` "
        "with Pieces support\n"
    )


def pieces_os_not_reachable_short() -> str:
    """Return the one-line Rich-markup readiness message.

    Safe to pass directly to ``rich.progress.Progress.update`` as the
    ``description`` keyword; must remain single-line (no ``\\n``).
    """
    return (
        "[red]Could not reach PiecesOS - try `pieces install`, "
        "then `pieces open`[/red]"
    )
