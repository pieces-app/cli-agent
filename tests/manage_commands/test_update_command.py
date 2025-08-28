"""
Tests for manage update command.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from pieces.command_interface.manage_commands.update_command import ManageUpdateCommand


class TestManageUpdateCommand:
    """Test the ManageUpdateCommand class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    def test_command_properties(self):
        """Test command basic properties."""
        assert self.command.get_name() == "update"
        assert "Update Pieces CLI" in self.command.get_help()
        assert len(self.command.get_examples()) > 0

    def test_add_arguments(self):
        """Test argument parsing setup."""
        parser = MagicMock()
        self.command.add_arguments(parser)
        parser.add_argument.assert_called_with(
            "--force",
            action="store_true",
            help="Force update even if already up to date",
        )


class TestCheckUpdates:
    """Test update checking functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch(
        "pieces.command_interface.manage_commands.update_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.update_command.check_updates_with_version_checker"
    )
    @patch("pieces.settings.Settings.logger")
    def test_check_updates_pip_available(
        self, mock_logger, mock_version_checker, mock_pypi
    ):
        """Test checking updates for pip installation with updates available."""
        mock_pypi.return_value = "1.2.0"
        mock_version_checker.return_value = True

        result = self.command._check_updates("pip")

        assert result is True
        mock_pypi.assert_called_once()
        mock_version_checker.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.update_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.update_command.check_updates_with_version_checker"
    )
    @patch("pieces.settings.Settings.logger")
    def test_check_updates_no_updates(
        self, mock_logger, mock_version_checker, mock_pypi
    ):
        """Test checking updates when no updates available."""
        mock_pypi.return_value = "1.0.0"
        mock_version_checker.return_value = False

        result = self.command._check_updates("pip")

        assert result is False

    @patch(
        "pieces.command_interface.manage_commands.update_command.get_latest_homebrew_version"
    )
    @patch("pieces.settings.Settings.logger")
    def test_check_updates_homebrew(self, mock_logger, mock_homebrew):
        """Test checking updates for Homebrew installation."""
        mock_homebrew.return_value = "1.2.0"

        with patch(
            "pieces.command_interface.manage_commands.update_command.check_updates_with_version_checker",
            return_value=True,
        ):
            result = self.command._check_updates("homebrew")

        assert result is True
        mock_homebrew.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.update_command.get_latest_pypi_version"
    )
    @patch("pieces.settings.Settings.logger")
    def test_check_updates_version_fetch_failed(self, mock_logger, mock_pypi):
        """Test when version fetching fails."""
        mock_pypi.return_value = None

        result = self.command._check_updates("pip")

        assert result is False

    @patch(
        "pieces.command_interface.manage_commands.update_command.get_latest_pypi_version"
    )
    @patch("pieces.settings.Settings.logger")
    def test_check_updates_unknown_source(self, mock_logger, mock_pypi):
        """Test checking updates for unknown source."""
        mock_pypi.return_value = "1.2.0"

        with patch(
            "pieces.command_interface.manage_commands.update_command.check_updates_with_version_checker",
            return_value=True,
        ):
            result = self.command._check_updates("unknown_source")

        assert result is True
        mock_pypi.assert_called_once()  # Should fallback to PyPI


class TestShouldUpdate:
    """Test update decision logic."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    def test_should_update_force_true(self):
        """Test should update when force is True."""
        result = self.command._should_update("pip", force=True)
        assert result is True

    @patch.object(ManageUpdateCommand, "_check_updates")
    def test_should_update_force_false(self, mock_check):
        """Test should update when force is False."""
        mock_check.return_value = True

        result = self.command._should_update("pip", force=False)

        assert result is True
        mock_check.assert_called_once_with("pip")


class TestValidateInstallerEnvironment:
    """Test installer environment validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch("pieces.settings.Settings.logger")
    def test_validate_installer_missing_venv(self, mock_logger):
        """Test validation when venv directory is missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                result, pip_path = self.command._validate_installer_environment()

                assert result == 1
                assert pip_path is None

    @patch("pieces.settings.Settings.logger")
    def test_validate_installer_missing_pip(self, mock_logger):
        """Test validation when pip executable is missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pieces_dir = Path(temp_dir) / ".pieces-cli"
            venv_dir = pieces_dir / "venv"
            venv_dir.mkdir(parents=True)

            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                result, pip_path = self.command._validate_installer_environment()

                assert result == 1
                assert pip_path is None

    @patch("pieces.settings.Settings.logger")
    def test_validate_installer_success(self, mock_logger):
        """Test successful installer environment validation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pieces_dir = Path(temp_dir) / ".pieces-cli"
            venv_dir = pieces_dir / "venv"
            bin_dir = venv_dir / ("Scripts" if sys.platform == "win32" else "bin")
            bin_dir.mkdir(parents=True)

            pip_exe = bin_dir / ("pip.exe" if sys.platform == "win32" else "pip")
            pip_exe.touch()

            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                result, pip_path = self.command._validate_installer_environment()

                assert result == 0
                assert pip_path == pip_exe


class TestPerformUpdate:
    """Test update execution."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_update_success(self, mock_logger, mock_run):
        """Test successful update execution."""
        mock_pip = Path("/test/pip")

        result = self.command._perform_update(mock_pip, force=False)

        assert result == 0
        assert mock_run.call_count == 2  # pip upgrade + pieces-cli upgrade

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_update_force(self, mock_logger, mock_run):
        """Test update execution with force flag."""
        mock_pip = Path("/test/pip")

        result = self.command._perform_update(mock_pip, force=True)

        assert result == 0
        # Check that --force-reinstall was added
        calls = mock_run.call_args_list
        assert "--force-reinstall" in calls[1][0][0]

    @patch("subprocess.run")
    @patch(
        "pieces.command_interface.manage_commands.update_command._handle_subprocess_error"
    )
    @patch("pieces.settings.Settings.logger")
    def test_perform_update_error(self, mock_logger, mock_error_handler, mock_run):
        """Test update execution with subprocess error."""
        mock_pip = Path("/test/pip")
        mock_run.side_effect = subprocess.CalledProcessError(1, "pip")
        mock_error_handler.return_value = 1

        result = self.command._perform_update(mock_pip, force=False)

        assert result == 1
        mock_error_handler.assert_called_once()


class TestVerifyUpdateSuccess:
    """Test update verification."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch("pieces.settings.Settings.logger")
    def test_verify_success(self, mock_logger):
        """Test verification of successful update."""
        result = self.command._verify_update_success(0)
        assert result == 0

    @patch("pieces.settings.Settings.logger")
    def test_verify_failure(self, mock_logger):
        """Test verification of failed update."""
        result = self.command._verify_update_success(1)
        assert result == 1


class TestInstallerVersionUpdate:
    """Test installer version update workflow."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch.object(ManageUpdateCommand, "_validate_installer_environment")
    @patch.object(ManageUpdateCommand, "_should_update")
    @patch.object(ManageUpdateCommand, "_perform_update")
    @patch.object(ManageUpdateCommand, "_verify_update_success")
    def test_update_installer_success(
        self, mock_verify, mock_perform, mock_should, mock_validate
    ):
        """Test successful installer update workflow."""
        mock_validate.return_value = (0, Path("/test/pip"))
        mock_should.return_value = True
        mock_perform.return_value = 0
        mock_verify.return_value = 0

        result = self.command._update_installer_version(force=False)

        assert result == 0
        mock_validate.assert_called_once()
        mock_should.assert_called_once_with("pip", False)
        mock_perform.assert_called_once_with(Path("/test/pip"), False)
        mock_verify.assert_called_once_with(0)

    @patch.object(ManageUpdateCommand, "_validate_installer_environment")
    def test_update_installer_validation_failed(self, mock_validate):
        """Test installer update when validation fails."""
        mock_validate.return_value = (1, None)

        result = self.command._update_installer_version(force=False)

        assert result == 1

    @patch.object(ManageUpdateCommand, "_validate_installer_environment")
    @patch.object(ManageUpdateCommand, "_should_update")
    def test_update_installer_no_updates(self, mock_should, mock_validate):
        """Test installer update when no updates needed."""
        mock_validate.return_value = (0, Path("/test/pip"))
        mock_should.return_value = False

        result = self.command._update_installer_version(force=False)

        assert result == 1


class TestHomebrewUpdate:
    """Test Homebrew update functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_homebrew_update_normal(self, mock_logger, mock_run):
        """Test normal Homebrew update."""
        result = self.command._perform_homebrew_update(force=False)

        assert result == 0
        mock_run.assert_called_once_with(["brew", "upgrade", "pieces-cli"], check=True)

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_homebrew_update_force(self, mock_logger, mock_run):
        """Test force Homebrew update."""
        result = self.command._perform_homebrew_update(force=True)

        assert result == 0
        mock_run.assert_called_once_with(
            ["brew", "reinstall", "pieces-cli"], check=True
        )

    @patch("subprocess.run")
    @patch(
        "pieces.command_interface.manage_commands.update_command._handle_subprocess_error"
    )
    @patch("pieces.settings.Settings.logger")
    def test_perform_homebrew_update_error(
        self, mock_logger, mock_error_handler, mock_run
    ):
        """Test Homebrew update with error."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "brew")
        mock_error_handler.return_value = 1

        result = self.command._perform_homebrew_update(force=False)

        assert result == 1


class TestPipUpdate:
    """Test pip update functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_pip_update_normal(self, mock_logger, mock_run):
        """Test normal pip update."""
        result = self.command._perform_pip_update(force=False)

        assert result == 0
        expected_cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pieces-cli",
        ]
        mock_run.assert_called_once_with(expected_cmd, check=True)

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_pip_update_force(self, mock_logger, mock_run):
        """Test force pip update."""
        result = self.command._perform_pip_update(force=True)

        assert result == 0
        expected_cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pieces-cli",
            "--force-reinstall",
        ]
        mock_run.assert_called_once_with(expected_cmd, check=True)


class TestChocolateyUpdate:
    """Test Chocolatey update functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_chocolatey_update_normal(self, mock_logger, mock_run):
        """Test normal Chocolatey update."""
        result = self.command._perform_chocolatey_update(force=False)

        assert result == 0
        expected_cmd = ["choco", "upgrade", "pieces-cli", "-y"]
        mock_run.assert_called_once_with(expected_cmd, check=True)

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_chocolatey_update_force(self, mock_logger, mock_run):
        """Test force Chocolatey update."""
        result = self.command._perform_chocolatey_update(force=True)

        assert result == 0
        expected_cmd = ["choco", "upgrade", "pieces-cli", "--force", "-y"]
        mock_run.assert_called_once_with(expected_cmd, check=True)


class TestWingetUpdate:
    """Test WinGet update functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_winget_update_normal(self, mock_logger, mock_run):
        """Test normal WinGet update."""
        result = self.command._perform_winget_update(force=False)

        assert result == 0
        expected_cmd = [
            "winget",
            "upgrade",
            "MeshIntelligentTechnologies.PiecesCLI",
            "--silent",
        ]
        mock_run.assert_called_once_with(expected_cmd, check=True)

    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_perform_winget_update_force(self, mock_logger, mock_run):
        """Test force WinGet update."""
        result = self.command._perform_winget_update(force=True)

        assert result == 0
        # Should call uninstall then install
        assert mock_run.call_count == 2


class TestVersionQueries:
    """Test version query methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch("subprocess.run")
    def test_get_latest_chocolatey_version(self, mock_run):
        """Test getting latest Chocolatey version."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "pieces-cli|1.2.3\nother-package|4.5.6"
        mock_run.return_value = mock_result

        result = self.command._get_latest_chocolatey_version()
        assert result == "1.2.3"

    @patch("subprocess.run")
    def test_get_latest_chocolatey_version_not_found(self, mock_run):
        """Test when Chocolatey package is not found."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = self.command._get_latest_chocolatey_version()
        assert result is None

    @patch("subprocess.run")
    def test_get_latest_winget_version(self, mock_run):
        """Test getting latest WinGet version."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Name  Id  Version\nPieces CLI  MeshIntelligentTechnologies.PiecesCLI  1.2.3"
        mock_run.return_value = mock_result

        result = self.command._get_latest_winget_version()
        assert result == "1.2.3"

    @patch("subprocess.run")
    def test_get_latest_winget_version_not_found(self, mock_run):
        """Test when WinGet package is not found."""
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        result = self.command._get_latest_winget_version()
        assert result is None


class TestExecuteCommand:
    """Test the main execute command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUpdateCommand()

    @patch(
        "pieces.command_interface.manage_commands.update_command._execute_operation_by_type"
    )
    def test_execute_with_force(self, mock_execute):
        """Test execute command with force flag."""
        mock_execute.return_value = 0

        result = self.command.execute(force=True)

        assert result == 0
        mock_execute.assert_called_once()
        # Check that operation map contains expected methods
        args, kwargs = mock_execute.call_args
        operation_map = args[0]

        assert "installer" in operation_map
        assert "homebrew" in operation_map
        assert "pip" in operation_map
        assert "chocolatey" in operation_map
        assert "winget" in operation_map
        assert kwargs["force"] is True

    @patch(
        "pieces.command_interface.manage_commands.update_command._execute_operation_by_type"
    )
    def test_execute_without_force(self, mock_execute):
        """Test execute command without force flag."""
        mock_execute.return_value = 0

        result = self.command.execute()

        assert result == 0
        args, kwargs = mock_execute.call_args
        assert kwargs["force"] is False

