"""
Tests for manage commands utilities.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from pieces.command_interface.manage_commands.utils import (
    _safe_subprocess_run,
    _check_command_availability,
    _get_executable_location,
    _detect_installer_method,
    _detect_homebrew_method,
    _detect_pip_method,
    _detect_chocolatey_method,
    _detect_winget_method,
    detect_installation_type,
    _get_fallback_method,
    _execute_operation_by_type,
    get_latest_pypi_version,
    get_latest_homebrew_version,
    check_updates_with_version_checker,
)


class TestSafeSubprocessRun:
    """Test safe subprocess execution."""

    def test_successful_run(self):
        """Test successful subprocess execution."""
        with patch("subprocess.run") as mock_run:
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = "success"
            mock_run.return_value = mock_result

            result = _safe_subprocess_run(["echo", "test"])

            assert result == mock_result
            mock_run.assert_called_once_with(
                ["echo", "test"], capture_output=True, text=True, check=False
            )

    def test_file_not_found_error(self):
        """Test handling of FileNotFoundError."""
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            result = _safe_subprocess_run(["nonexistent", "command"])
            assert result is None

    def test_called_process_error(self):
        """Test handling of CalledProcessError."""
        with patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "cmd")
        ):
            result = _safe_subprocess_run(["failing", "command"])
            assert result is None


class TestCommandAvailability:
    """Test command availability checking."""

    def test_command_exists(self):
        """Test detecting existing command."""
        with patch("shutil.which", return_value="/usr/bin/brew"):
            assert _check_command_availability("brew") is True

    def test_command_not_exists(self):
        """Test detecting non-existing command."""
        with patch("shutil.which", return_value=None):
            assert _check_command_availability("nonexistent") is False


class TestExecutableLocation:
    """Test executable location detection."""

    def test_finds_pieces_executable(self):
        """Test finding pieces executable using sys.argv[0]."""
        test_path = "/usr/local/bin/pieces"
        with patch("sys.argv", [test_path, "manage", "status"]):
            with patch("shutil.which", return_value=None):  # Disable PATH fallback
                result = _get_executable_location()
                # Convert expected path to absolute path for platform compatibility
                expected = Path(os.path.abspath(test_path))
                assert result == expected

    def test_executable_not_found(self):
        """Test when sys.argv is empty and no fallbacks work."""
        with patch("sys.argv", []):
            with patch("shutil.which", return_value=None):
                with patch("pathlib.Path.exists", return_value=False):
                    result = _get_executable_location()
                    assert result is None

    def test_finds_pieces_via_path(self):
        """Test finding pieces executable via PATH when sys.argv[0] is a Python file."""
        with patch("sys.argv", ["/path/to/python/script.py", "manage", "status"]):
            with patch("shutil.which", return_value="/usr/local/bin/pieces"):
                result = _get_executable_location()
                assert result == Path("/usr/local/bin/pieces")

    def test_finds_pieces_via_path_fallback(self):
        """Test finding pieces executable via PATH as fallback."""
        with patch("sys.argv", []):  # Empty sys.argv
            with patch("shutil.which", return_value="/usr/local/bin/pieces"):
                result = _get_executable_location()
                assert result == Path("/usr/local/bin/pieces")

    def test_finds_pieces_in_installer_structure(self):
        """Test finding pieces in installer directory structure."""
        installer_dir = Path.home() / ".pieces-cli"
        wrapper_script = installer_dir / "pieces"

        # Create a mock file path that would be inside the installer structure
        mock_file_path = str(
            installer_dir
            / "venv/lib/python3.11/site-packages/pieces/command_interface/manage_commands/utils.py"
        )

        with patch("sys.argv", []):
            with patch("shutil.which", return_value=None):
                with patch(
                    "pieces.command_interface.manage_commands.utils.__file__",
                    mock_file_path,
                ):
                    # Mock Path.exists to return True only for our wrapper script
                    def mock_exists(self):
                        return self == wrapper_script

                    with patch("pathlib.Path.exists", mock_exists):
                        result = _get_executable_location()
                        assert result == wrapper_script

    def test_finds_pieces_relative_to_python(self):
        """Test finding pieces executable relative to current Python."""
        python_dir = Path(sys.executable).parent
        pieces_executable = python_dir / "pieces"

        with patch("sys.argv", []):
            with patch("shutil.which", return_value=None):
                # Mock Path.exists to return True only for our pieces executable
                def mock_exists(self):
                    return self == pieces_executable

                with patch("pathlib.Path.exists", mock_exists):
                    result = _get_executable_location()
                    assert result == pieces_executable

    def test_exception_handling(self):
        """Test exception handling during detection."""
        with patch("os.path.abspath", side_effect=Exception("Test error")):
            result = _get_executable_location()
            assert result is None


class TestInstallerDetection:
    """Test installer method detection."""

    def test_detects_installer_directory(self):
        """Test detecting installer via directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pieces_dir = Path(temp_dir) / ".pieces-cli"
            venv_dir = pieces_dir / "venv"
            venv_dir.mkdir(parents=True)

            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                assert _detect_installer_method() is True

    def test_no_installer_directory(self):
        """Test when installer directory doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                assert _detect_installer_method() is False

    def test_environment_variable_detection(self):
        """Test detection via environment variable."""
        test_path = "/home/user/.pieces-cli"
        with patch.dict(os.environ, {"PIECES_CLI_HOME": test_path}):
            with patch("pathlib.Path.home") as mock_home:
                mock_home.return_value = Path("/home/user")
                assert _detect_installer_method() is True


class TestHomebrewDetection:
    """Test Homebrew installation detection."""

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    @patch("pieces.command_interface.manage_commands.utils._safe_subprocess_run")
    def test_detects_homebrew_list(self, mock_subprocess, mock_command_check):
        """Test detecting Homebrew via brew list command."""
        mock_command_check.return_value = True
        mock_result = Mock()
        mock_result.returncode = 0
        mock_subprocess.return_value = mock_result

        assert _detect_homebrew_method() is True
        mock_subprocess.assert_called_with(["brew", "list", "pieces-cli"])

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    def test_brew_not_available(self, mock_command_check):
        """Test when brew command is not available."""
        mock_command_check.return_value = False
        assert _detect_homebrew_method() is False

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    @patch("pieces.command_interface.manage_commands.utils._get_executable_location")
    def test_detects_homebrew_path(self, mock_exe_location, mock_command_check):
        """Test detecting Homebrew via executable path."""
        mock_command_check.return_value = True
        mock_exe_location.return_value = Path("/opt/homebrew/bin/pieces")

        with patch(
            "pieces.command_interface.manage_commands.utils._safe_subprocess_run"
        ) as mock_subprocess:
            mock_subprocess.return_value = Mock(returncode=1)  # brew list fails

            assert _detect_homebrew_method() is True


class TestPipDetection:
    """Test pip installation detection."""

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    @patch("pieces.command_interface.manage_commands.utils._safe_subprocess_run")
    def test_detects_pip_installation(self, mock_subprocess, mock_command_check):
        """Test detecting pip installation."""
        # Make the first command (sys.executable) succeed
        mock_command_check.side_effect = lambda cmd: cmd == sys.executable or cmd in [
            "python",
            "pip",
        ]

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Location: /usr/local/lib/python3.9/site-packages"
        mock_subprocess.return_value = mock_result

        result = _detect_pip_method()

        assert result["detected"] is True
        assert result["user_install"] is False
        assert result["venv"] is False

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    @patch("pieces.command_interface.manage_commands.utils._safe_subprocess_run")
    def test_detects_user_installation(self, mock_subprocess, mock_command_check):
        """Test detecting pip user installation."""
        # Make the first command (sys.executable) succeed
        mock_command_check.side_effect = lambda cmd: cmd == sys.executable or cmd in [
            "python"
        ]

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Location: /home/user/.local/lib/python3.9/site-packages"
        mock_subprocess.return_value = mock_result

        result = _detect_pip_method()

        assert result["detected"] is True
        assert result["user_install"] is True

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    @patch("pieces.command_interface.manage_commands.utils._safe_subprocess_run")
    def test_detects_venv_installation(self, mock_subprocess, mock_command_check):
        """Test detecting pip virtual environment installation."""
        # Make the first command (sys.executable) succeed
        mock_command_check.side_effect = lambda cmd: cmd == sys.executable or cmd in [
            "python"
        ]

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Location: /home/user/venv/lib/python3.9/site-packages"
        mock_subprocess.return_value = mock_result

        result = _detect_pip_method()

        assert result["detected"] is True
        assert result["venv"] is True

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    def test_no_pip_detected(self, mock_command_check):
        """Test when no pip installation is detected."""
        mock_command_check.return_value = False

        result = _detect_pip_method()

        assert result["detected"] is False


class TestChocolateyDetection:
    """Test Chocolatey installation detection."""

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    @patch("pieces.command_interface.manage_commands.utils._safe_subprocess_run")
    def test_detects_chocolatey(self, mock_subprocess, mock_command_check):
        """Test detecting Chocolatey installation."""
        mock_command_check.return_value = True
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "pieces-cli 1.0.0"
        mock_subprocess.return_value = mock_result

        assert _detect_chocolatey_method() is True

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    def test_choco_not_available(self, mock_command_check):
        """Test when choco command is not available."""
        mock_command_check.return_value = False
        assert _detect_chocolatey_method() is False


class TestWingetDetection:
    """Test WinGet installation detection."""

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    @patch("pieces.command_interface.manage_commands.utils._safe_subprocess_run")
    def test_detects_winget(self, mock_subprocess, mock_command_check):
        """Test detecting WinGet installation."""
        mock_command_check.return_value = True
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "MeshIntelligentTechnologies.PiecesCLI  1.0.0"
        mock_subprocess.return_value = mock_result

        assert _detect_winget_method() is True

    @patch("pieces.command_interface.manage_commands.utils._check_command_availability")
    def test_winget_not_available(self, mock_command_check):
        """Test when winget command is not available."""
        mock_command_check.return_value = False
        assert _detect_winget_method() is False


class TestInstallationTypeDetection:
    """Test overall installation type detection."""

    def test_manual_override(self):
        """Test manual override via environment variable."""
        with patch.dict(os.environ, {"PIECES_CLI_INSTALLATION_TYPE": "homebrew"}):
            with patch("pieces.settings.Settings.logger"):
                result = detect_installation_type()
                assert result == "homebrew"

    @patch("pieces.command_interface.manage_commands.utils._detect_installer_method")
    def test_detects_installer(self, mock_installer):
        """Test detecting installer method."""
        mock_installer.return_value = True

        with patch("pieces.settings.Settings.logger"):
            result = detect_installation_type()
            assert result == "installer"

    @patch("pieces.command_interface.manage_commands.utils._detect_installer_method")
    @patch("pieces.command_interface.manage_commands.utils._detect_homebrew_method")
    def test_detects_homebrew(self, mock_homebrew, mock_installer):
        """Test detecting Homebrew method."""
        mock_installer.return_value = False
        mock_homebrew.return_value = True

        with patch("pieces.settings.Settings.logger"):
            result = detect_installation_type()
            assert result == "homebrew"

    @patch("pieces.command_interface.manage_commands.utils._detect_installer_method")
    @patch("pieces.command_interface.manage_commands.utils._detect_homebrew_method")
    @patch("pieces.command_interface.manage_commands.utils._detect_chocolatey_method")
    @patch("pieces.command_interface.manage_commands.utils._detect_winget_method")
    @patch("pieces.command_interface.manage_commands.utils._detect_pip_method")
    def test_detects_unknown(
        self, mock_pip, mock_winget, mock_choco, mock_homebrew, mock_installer
    ):
        """Test detecting unknown installation method."""
        mock_installer.return_value = False
        mock_homebrew.return_value = False
        mock_choco.return_value = False
        mock_winget.return_value = False
        mock_pip.return_value = {"detected": False}

        with patch("pieces.settings.Settings.logger"):
            result = detect_installation_type()
            assert result == "unknown"


class TestFallbackMethods:
    """Test fallback method selection."""

    def test_unknown_fallback(self):
        """Test fallback for unknown installation type."""
        operation_map = {"pip": lambda: "pip_op", "homebrew": lambda: "brew_op"}
        result = _get_fallback_method("unknown", operation_map)
        assert result == "pip"

    def test_no_fallback_available(self):
        """Test when no fallback is available."""
        operation_map = {"homebrew": lambda: "brew_op"}
        result = _get_fallback_method("unknown", operation_map)
        assert result is None

    def test_invalid_installation_type(self):
        """Test invalid installation type."""
        operation_map = {"pip": lambda: "pip_op"}
        result = _get_fallback_method("invalid", operation_map)
        assert result is None


class TestExecuteOperationByType:
    """Test operation execution by installation type."""

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch("pieces.settings.Settings.logger")
    def test_executes_primary_method(self, mock_logger, mock_detect):
        """Test executing primary installation method."""
        mock_detect.return_value = "pip"
        operation_map = {"pip": Mock(return_value=0)}

        result = _execute_operation_by_type(operation_map, test_arg="value")

        assert result == 0
        operation_map["pip"].assert_called_once_with(test_arg="value")

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch("pieces.command_interface.manage_commands.utils._get_fallback_method")
    @patch("pieces.settings.Settings.logger")
    def test_executes_fallback_method(self, mock_logger, mock_fallback, mock_detect):
        """Test executing fallback method."""
        mock_detect.return_value = "unknown"
        mock_fallback.return_value = "pip"
        operation_map = {"pip": Mock(return_value=0)}

        result = _execute_operation_by_type(operation_map, test_arg="value")

        assert result == 0
        operation_map["pip"].assert_called_once_with(test_arg="value")

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch("pieces.command_interface.manage_commands.utils._get_fallback_method")
    @patch("pieces.settings.Settings.logger")
    def test_no_supported_method(self, mock_logger, mock_fallback, mock_detect):
        """Test when no supported method is available."""
        mock_detect.return_value = "unsupported"
        mock_fallback.return_value = None
        operation_map = {"pip": Mock(return_value=0)}

        result = _execute_operation_by_type(operation_map)

        assert result == 1

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch("pieces.settings.Settings.logger")
    def test_handles_exceptions(self, mock_logger, mock_detect):
        """Test exception handling."""
        mock_detect.side_effect = Exception("Test error")
        operation_map = {"pip": Mock(return_value=0)}

        result = _execute_operation_by_type(operation_map)

        assert result == 1


class TestVersionChecking:
    """Test version checking utilities."""

    @patch("urllib.request.urlopen")
    def test_get_latest_pypi_version(self, mock_urlopen):
        """Test getting latest PyPI version."""
        mock_response = Mock()
        mock_response.read.return_value = json.dumps(
            {"info": {"version": "1.2.3"}}
        ).encode()
        mock_urlopen.return_value.__enter__.return_value = mock_response

        result = get_latest_pypi_version()
        assert result == "1.2.3"

    @patch("urllib.request.urlopen")
    def test_pypi_version_error(self, mock_urlopen):
        """Test PyPI version check error handling."""
        mock_urlopen.side_effect = Exception("Network error")

        with patch("pieces.settings.Settings.logger"):
            result = get_latest_pypi_version()
            assert result is None

    @patch("subprocess.run")
    def test_get_latest_homebrew_version(self, mock_run):
        """Test getting latest Homebrew version."""
        mock_result = Mock()
        mock_result.stdout = json.dumps([{"versions": {"stable": "1.2.3"}}])
        mock_run.return_value = mock_result

        result = get_latest_homebrew_version()
        assert result == "1.2.3"

    @patch("subprocess.run")
    def test_homebrew_version_error(self, mock_run):
        """Test Homebrew version check error handling."""
        mock_run.side_effect = Exception("Brew error")

        result = get_latest_homebrew_version()
        assert result is None

    @patch(
        "pieces._vendor.pieces_os_client.wrapper.version_compatibility.VersionChecker.compare"
    )
    def test_check_updates_available(self, mock_compare):
        """Test checking for available updates."""
        mock_compare.return_value = -1  # Current version is older

        result = check_updates_with_version_checker("1.0.0", "1.1.0")
        assert result is True

    @patch(
        "pieces._vendor.pieces_os_client.wrapper.version_compatibility.VersionChecker.compare"
    )
    def test_check_no_updates(self, mock_compare):
        """Test when no updates are available."""
        mock_compare.return_value = 0  # Same version

        result = check_updates_with_version_checker("1.0.0", "1.0.0")
        assert result is False

    def test_check_updates_unknown_version(self):
        """Test version checking with unknown versions."""
        result = check_updates_with_version_checker("unknown", "1.0.0")
        assert result is False

        result = check_updates_with_version_checker("1.0.0", "unknown")
        assert result is False

    @patch(
        "pieces._vendor.pieces_os_client.wrapper.version_compatibility.VersionChecker.compare"
    )
    def test_check_updates_error(self, mock_compare):
        """Test version checking error handling."""
        mock_compare.side_effect = Exception("Version compare error")

        result = check_updates_with_version_checker("1.0.0", "1.1.0")
        assert result is False
