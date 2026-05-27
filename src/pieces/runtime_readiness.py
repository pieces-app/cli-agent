from __future__ import annotations


def pieces_os_not_ready_lines(context: str | None = None) -> list[str]:
    if context:
        headline = f"❌ PiecesOS is not reachable while {context}."
    else:
        headline = "❌ PiecesOS is not reachable from Pieces CLI."

    return [
        headline,
        "PiecesOS may be uninstalled, not running, still starting, or failing local readiness/port discovery.",
        "Try:",
        "  1. Run `pieces install` to install or repair PiecesOS.",
        "  2. Run `pieces open --pieces_os` or open/restart PiecesOS, then retry.",
        "  3. If this keeps happening, copy `pieces version` output and share it with support.",
    ]


def print_pieces_os_not_ready(context: str | None = None) -> None:
    from pieces.settings import Settings

    for line in pieces_os_not_ready_lines(context):
        Settings.logger.print(line)
