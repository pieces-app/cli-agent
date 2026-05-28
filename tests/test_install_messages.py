"""Tests for ``src/pieces/install_messages.py``.

These pin the wording contract of the install messages so macOS/Windows stop
overclaiming "Installed ... successfully" when the CLI only downloaded the
package and launched the OS installer. They also guard the call site against
reintroducing the old overclaiming string, and assert the helper module has no
circular-import surface (stdlib-only, no ``pieces.*`` imports).
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest

from pieces.install_messages import (
    install_completed_message,
    install_failed_message,
)


REPO_ROOT = Path(__file__).resolve().parents[1]

# The legacy overclaiming string that must not reappear at the call site.
FORBIDDEN_LEGACY_STRING = "✅ Installed PiecesOS successfully"

CALL_SITE_PATH = "src/pieces/core/install_pieces_os.py"


class TestInstallCompletedMessage:
    """Wording assertions for the per-OS success message."""

    @pytest.mark.parametrize("system", ["Darwin", "Windows"])
    def test_macos_windows_say_downloaded_not_installed(self, system):
        msg = install_completed_message(system)
        assert "Downloaded PiecesOS" in msg
        assert "pieces open" in msg
        # Must not overclaim a finished install on these platforms.
        assert "Installed PiecesOS successfully" not in msg

    @pytest.mark.parametrize("system", ["Darwin", "Windows"])
    def test_macos_windows_point_at_opened_installer(self, system):
        assert "window that just opened" in install_completed_message(system)

    def test_linux_says_installed(self):
        msg = install_completed_message("Linux")
        assert "Installed PiecesOS" in msg
        assert "pieces open" in msg

    def test_linux_differs_from_macos(self):
        assert install_completed_message("Linux") != install_completed_message(
            "Darwin"
        )

    def test_unknown_platform_falls_back_to_download_wording(self):
        # Anything that is not Linux is treated as the download/launch flow.
        assert "Downloaded PiecesOS" in install_completed_message("Plan9")

    def test_returns_single_line(self):
        for system in ("Linux", "Darwin", "Windows"):
            assert "\n" not in install_completed_message(system)


class TestInstallFailedMessage:
    """Wording assertions for the failure message."""

    def test_mentions_manual_install_page_in_browser(self):
        msg = install_failed_message()
        assert "manual install page" in msg
        assert "browser" in msg

    def test_does_not_overclaim_success(self):
        assert "Installed PiecesOS successfully" not in install_failed_message()

    def test_returns_single_line(self):
        assert "\n" not in install_failed_message()


def test_call_site_drops_legacy_overclaim_string():
    """Regression guard: the install command call site must not reintroduce
    the overclaiming legacy success string. Use the helper instead.
    """
    contents = (REPO_ROOT / CALL_SITE_PATH).read_text(encoding="utf-8")
    assert FORBIDDEN_LEGACY_STRING not in contents, (
        f"{CALL_SITE_PATH} reintroduced the overclaiming legacy string "
        f"{FORBIDDEN_LEGACY_STRING!r}. Use the helpers in "
        f"src/pieces/install_messages.py instead."
    )


def test_import_smoke_no_circular():
    """Importing the helper in a fresh interpreter must not raise.

    Runs in a subprocess so session module caching cannot mask a real cycle.
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
        [sys.executable, "-c", "import pieces.install_messages"],
        capture_output=True,
        text=True,
        env=env,
    )

    assert result.returncode == 0, (
        f"import regression detected\n"
        f"stdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
