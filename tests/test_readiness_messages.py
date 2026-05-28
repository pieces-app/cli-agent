"""Tests for ``src/pieces/readiness_messages.py``.

These tests pin the wording contract of the two readiness helpers,
guard against a circular-import regression between ``pieces.settings``
and the ``pieces.core`` submodules that import ``Settings`` at module
top, and assert the three in-scope call sites do not reintroduce the
old vague/overclaiming strings.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from pieces.readiness_messages import (
    pieces_os_not_reachable,
    pieces_os_not_reachable_short,
)


REPO_ROOT = Path(__file__).resolve().parents[1]

# The three in-scope call sites that were updated to use the readiness
# helpers. Out-of-scope locations (vendored SDK, MCP gateway) are
# intentionally not listed here because they live behind a different
# review boundary.
EDITED_CALL_SITE_PATHS = (
    "src/pieces/core/open_command.py",
    "src/pieces/core/onboarding.py",
    "src/pieces/settings.py",
)

# Overclaiming legacy strings that the readiness helpers replaced.
# These must not reappear in any of the edited call sites.
FORBIDDEN_LEGACY_STRINGS = (
    "PiecesOS is not running",
    "PiecesOS is not installed",
)


class TestPiecesOSNotReachable:
    """Wording assertions for the long-form Markdown helper."""

    def test_contains_pieces_install(self):
        assert "pieces install" in pieces_os_not_reachable()

    def test_contains_pieces_open(self):
        assert "pieces open" in pieces_os_not_reachable()

    def test_contains_pieces_version(self):
        assert "pieces version" in pieces_os_not_reachable()

    def test_contains_retry_case_insensitive(self):
        assert "retry" in pieces_os_not_reachable().lower()

    def test_does_not_mention_port_txt(self):
        assert ".port.txt" not in pieces_os_not_reachable()

    def test_does_not_overclaim_install_state(self):
        # The CLI cannot distinguish "not installed" from
        # "installed but not running" via open_pieces_os() alone.
        assert "is not installed" not in pieces_os_not_reachable()


class TestPiecesOSNotReachableShort:
    """Wording and shape assertions for the short-form Rich-markup helper."""

    def test_returns_single_line(self):
        # Must be safe to drop into Rich Progress description=...
        assert "\n" not in pieces_os_not_reachable_short()

    def test_does_not_mention_port_txt(self):
        assert ".port.txt" not in pieces_os_not_reachable_short()

    def test_does_not_overclaim_install_state(self):
        assert "is not installed" not in pieces_os_not_reachable_short()

    def test_contains_pieces_install(self):
        assert "pieces install" in pieces_os_not_reachable_short()

    def test_contains_pieces_open(self):
        assert "pieces open" in pieces_os_not_reachable_short()


def test_import_smoke_no_circular():
    """Regression guard: importing settings, the two edited core call
    sites, and the new helper in a single fresh interpreter must not
    raise ``ImportError`` from a circular import.

    Runs in a subprocess so module caching from the test session cannot
    mask a real cycle.
    """
    src_dir = REPO_ROOT / "src"

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{src_dir}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else str(src_dir)
    )

    result = subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import pieces.settings, pieces.core.open_command, "
                "pieces.core.onboarding, pieces.readiness_messages"
            ),
        ],
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (
        f"circular-import regression detected\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )


@pytest.mark.parametrize("relative_path", EDITED_CALL_SITE_PATHS)
@pytest.mark.parametrize("forbidden", FORBIDDEN_LEGACY_STRINGS)
def test_edited_call_sites_drop_legacy_overclaim_strings(
    relative_path: str, forbidden: str
) -> None:
    """Regression guard: the three call sites we replaced with the
    readiness helpers must not reintroduce the overclaiming legacy
    strings.

    Scope: only the three in-scope edited files. Vendored SDK and MCP
    gateway sites live behind a different review boundary and are not
    asserted here.
    """
    file_path = REPO_ROOT / relative_path
    contents = file_path.read_text(encoding="utf-8")

    assert forbidden not in contents, (
        f"{relative_path} reintroduced the overclaiming legacy string "
        f"{forbidden!r}. Use the helpers in "
        f"src/pieces/readiness_messages.py instead."
    )
