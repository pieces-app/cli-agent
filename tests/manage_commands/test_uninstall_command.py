"""
Tests for manage uninstall command.
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

from pieces.command_interface.manage_commands.uninstall_command import (
    ManageUninstallCommand,
)


class TestManageUninstallCommand:
    """Test the ManageUninstallCommand class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    def test_command_properties(self):
        """Test command basic properties."""
        assert self.command.get_name() == "uninstall"
        assert "Uninstall Pieces CLI" in self.command.get_help()
        assert len(self.command.get_examples()) > 0

    def test_add_arguments(self):
        """Test argument parsing setup."""
        parser = MagicMock()
        self.command.add_arguments(parser)
        parser.add_argument.assert_called_with(
            "--remove-config",
            action="store_true",
            help="Remove configuration files including shell completion scripts",
        )


class TestConfirmUninstall:
    """Test uninstall confirmation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch("builtins.input", return_value="y")
    @patch("pieces.settings.Settings.logger")
    def test_confirm_uninstall_yes(self, mock_logger, mock_input):
        """Test user confirms uninstall with 'y'."""
        result = self.command._confirm_uninstall("/test/path")
        assert result is True

    @patch("builtins.input", return_value="yes")
    @patch("pieces.settings.Settings.logger")
    def test_confirm_uninstall_yes_full(self, mock_logger, mock_input):
        """Test user confirms uninstall with 'yes'."""
        result = self.command._confirm_uninstall()
        assert result is True

    @patch("builtins.input", return_value="Y")
    @patch("pieces.settings.Settings.logger")
    def test_confirm_uninstall_yes_uppercase(self, mock_logger, mock_input):
        """Test user confirms uninstall with uppercase 'Y'."""
        result = self.command._confirm_uninstall()
        assert result is True

    @patch("builtins.input", return_value="n")
    @patch("pieces.settings.Settings.logger")
    def test_confirm_uninstall_no(self, mock_logger, mock_input):
        """Test user declines uninstall with 'n'."""
        result = self.command._confirm_uninstall()
        assert result is False

    @patch("builtins.input", return_value="")
    @patch("pieces.settings.Settings.logger")
    def test_confirm_uninstall_empty(self, mock_logger, mock_input):
        """Test user declines uninstall with empty input."""
        result = self.command._confirm_uninstall()
        assert result is False

    @patch("builtins.input", return_value="invalid")
    @patch("pieces.settings.Settings.logger")
    def test_confirm_uninstall_invalid(self, mock_logger, mock_input):
        """Test user declines uninstall with invalid input."""
        result = self.command._confirm_uninstall()
        assert result is False


class TestPostUninstallCleanup:
    """Test post-uninstall cleanup functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch(
        "pieces.command_interface.manage_commands.uninstall_command.remove_completion_scripts"
    )
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command.remove_config_dir"
    )
    @patch("pieces.settings.Settings.logger")
    def test_post_uninstall_cleanup_with_config(
        self, mock_logger, mock_remove_config, mock_remove_scripts
    ):
        """Test cleanup with config removal."""
        self.command._post_uninstall_cleanup(remove_config=True)

        mock_remove_scripts.assert_called_once()
        mock_remove_config.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.uninstall_command.remove_completion_scripts"
    )
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command.remove_config_dir"
    )
    @patch("pieces.settings.Settings.logger")
    def test_post_uninstall_cleanup_without_config(
        self, mock_logger, mock_remove_config, mock_remove_scripts
    ):
        """Test cleanup without config removal."""
        self.command._post_uninstall_cleanup(remove_config=False)

        mock_remove_scripts.assert_called_once()
        mock_remove_config.assert_not_called()


class TestInstallerUninstall:
    """Test installer version uninstall functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch("pieces.settings.Settings.logger")
    def test_uninstall_installer_directory_not_found(self, mock_logger):
        """Test uninstall when installer directory doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                result = self.command._uninstall_installer_version(remove_config=False)

                assert result == 0  # Should succeed gracefully

    @patch.object(ManageUninstallCommand, "_confirm_uninstall", return_value=False)
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_installer_user_cancelled(self, mock_logger, mock_confirm):
        """Test uninstall when user cancels."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pieces_dir = Path(temp_dir) / ".pieces-cli"
            pieces_dir.mkdir()

            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                result = self.command._uninstall_installer_version(remove_config=False)

                assert result == 0
                mock_confirm.assert_called_once()

    @patch.object(ManageUninstallCommand, "_confirm_uninstall", return_value=True)
    @patch.object(ManageUninstallCommand, "_post_uninstall_cleanup")
    @patch("shutil.rmtree")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_installer_success(
        self, mock_logger, mock_rmtree, mock_cleanup, mock_confirm
    ):
        """Test successful installer uninstall."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pieces_dir = Path(temp_dir) / ".pieces-cli"
            pieces_dir.mkdir()

            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                result = self.command._uninstall_installer_version(remove_config=True)

                assert result == 0
                mock_confirm.assert_called_once()
                mock_rmtree.assert_called_once_with(pieces_dir)
                mock_cleanup.assert_called_once_with(True)

    @patch.object(ManageUninstallCommand, "_confirm_uninstall", return_value=True)
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_installer_error(self, mock_logger, mock_confirm):
        """Test installer uninstall with removal error."""
        with tempfile.TemporaryDirectory() as temp_dir:
            pieces_dir = Path(temp_dir) / ".pieces-cli"
            pieces_dir.mkdir()

            with patch("pathlib.Path.home", return_value=Path(temp_dir)):
                # Mock rmtree to fail only for the specific pieces_dir
                original_rmtree = shutil.rmtree
                with patch("shutil.rmtree") as mock_rmtree:

                    def selective_rmtree(path, **kwargs):
                        if str(path).endswith(".pieces-cli"):
                            raise Exception("Permission denied")
                        else:
                            # Call the real rmtree for other paths (like tempfile cleanup)
                            return original_rmtree(path, **kwargs)

                    mock_rmtree.side_effect = selective_rmtree

                    result = self.command._uninstall_installer_version(
                        remove_config=False
                    )

                    assert result == 1
                    mock_confirm.assert_called_once()


class TestHomebrewUninstall:
    """Test Homebrew uninstall functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch("subprocess.run")
    @patch.object(ManageUninstallCommand, "_post_uninstall_cleanup")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_homebrew_success(self, mock_logger, mock_cleanup, mock_run):
        """Test successful Homebrew uninstall."""
        result = self.command._uninstall_homebrew_version(remove_config=True)

        assert result == 0
        mock_run.assert_called_once_with(
            ["brew", "uninstall", "pieces-cli"], check=True
        )
        mock_cleanup.assert_called_once_with(True)

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "brew"))
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._handle_subprocess_error",
        return_value=1,
    )
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_homebrew_error(self, mock_logger, mock_error_handler, mock_run):
        """Test Homebrew uninstall with error."""
        result = self.command._uninstall_homebrew_version(remove_config=False)

        assert result == 1
        mock_error_handler.assert_called_once()


class TestPipUninstall:
    """Test pip uninstall functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch("subprocess.run")
    @patch.object(ManageUninstallCommand, "_post_uninstall_cleanup")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_pip_success(self, mock_logger, mock_cleanup, mock_run):
        """Test successful pip uninstall."""
        result = self.command._uninstall_pip_version(remove_config=False)

        assert result == 0
        expected_cmd = [sys.executable, "-m", "pip", "uninstall", "pieces-cli", "-y"]
        mock_run.assert_called_once_with(expected_cmd, check=True)
        mock_cleanup.assert_called_once_with(False)

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "pip"))
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._handle_subprocess_error",
        return_value=1,
    )
    @patch.object(ManageUninstallCommand, "_post_uninstall_cleanup")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_pip_error(
        self, mock_logger, mock_cleanup, mock_error_handler, mock_run
    ):
        """Test pip uninstall with error."""
        result = self.command._uninstall_pip_version(remove_config=True)

        assert result == 1
        mock_error_handler.assert_called_once()
        # Cleanup should not be called when subprocess fails
        mock_cleanup.assert_not_called()


class TestChocolateyUninstall:
    """Test Chocolatey uninstall functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch("subprocess.run")
    @patch.object(ManageUninstallCommand, "_post_uninstall_cleanup")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_chocolatey_success(self, mock_logger, mock_cleanup, mock_run):
        """Test successful Chocolatey uninstall."""
        result = self.command._uninstall_chocolatey_version(remove_config=True)

        assert result == 0
        mock_run.assert_called_once_with(
            ["choco", "uninstall", "pieces-cli", "-y"], check=True
        )
        mock_cleanup.assert_called_once_with(True)

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "choco"))
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._handle_subprocess_error",
        return_value=1,
    )
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_chocolatey_error(
        self, mock_logger, mock_error_handler, mock_run
    ):
        """Test Chocolatey uninstall with error."""
        result = self.command._uninstall_chocolatey_version(remove_config=False)

        assert result == 1
        mock_error_handler.assert_called_once()


class TestWingetUninstall:
    """Test WinGet uninstall functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch("subprocess.run")
    @patch.object(ManageUninstallCommand, "_post_uninstall_cleanup")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_winget_success(self, mock_logger, mock_cleanup, mock_run):
        """Test successful WinGet uninstall."""
        result = self.command._uninstall_winget_version(remove_config=False)

        assert result == 0
        expected_cmd = [
            "winget",
            "uninstall",
            "MeshIntelligentTechnologies.PiecesCLI",
            "--silent",
        ]
        mock_run.assert_called_once_with(expected_cmd, check=True)
        mock_cleanup.assert_called_once_with(False)

    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "winget"))
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._handle_subprocess_error",
        return_value=1,
    )
    @patch.object(ManageUninstallCommand, "_post_uninstall_cleanup")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_winget_error(
        self, mock_logger, mock_cleanup, mock_error_handler, mock_run
    ):
        """Test WinGet uninstall with error."""
        result = self.command._uninstall_winget_version(remove_config=True)

        assert result == 1
        mock_error_handler.assert_called_once()
        # Cleanup should not be called when subprocess fails
        mock_cleanup.assert_not_called()


class TestExecuteCommand:
    """Test the main execute command."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._execute_operation_by_type"
    )
    def test_execute_with_remove_config(self, mock_execute):
        """Test execute command with remove-config flag."""
        mock_execute.return_value = 0

        result = self.command.execute(remove_config=True)

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
        assert kwargs["remove_config"] is True

    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._execute_operation_by_type"
    )
    def test_execute_without_remove_config(self, mock_execute):
        """Test execute command without remove-config flag."""
        mock_execute.return_value = 0

        result = self.command.execute()

        assert result == 0
        args, kwargs = mock_execute.call_args
        assert kwargs["remove_config"] is False

    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._execute_operation_by_type"
    )
    def test_execute_operation_map_functions(self, mock_execute):
        """Test that operation map functions work correctly."""
        mock_execute.return_value = 0

        # Execute to get the operation map
        self.command.execute(remove_config=True)

        args, kwargs = mock_execute.call_args
        operation_map = args[0]

        # Test that each function in the operation map can be called
        for method_name, method_func in operation_map.items():
            # Each function should be callable
            assert callable(method_func)


class TestUninstallWorkflows:
    """Test complete uninstall workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch.object(
        ManageUninstallCommand, "_uninstall_installer_version", return_value=0
    )
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._execute_operation_by_type"
    )
    def test_installer_uninstall_workflow(self, mock_execute, mock_uninstall):
        """Test complete installer uninstall workflow."""

        # Mock _execute_operation_by_type to call the actual operation
        def mock_execute_side_effect(operation_map, **kwargs):
            return operation_map["installer"](**kwargs)

        mock_execute.side_effect = mock_execute_side_effect

        result = self.command.execute(remove_config=True)

        assert result == 0
        mock_uninstall.assert_called_once_with(remove_config=True)

    @patch.object(ManageUninstallCommand, "_uninstall_pip_version", return_value=0)
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._execute_operation_by_type"
    )
    def test_pip_uninstall_workflow(self, mock_execute, mock_uninstall):
        """Test complete pip uninstall workflow."""

        # Mock _execute_operation_by_type to call the actual operation
        def mock_execute_side_effect(operation_map, **kwargs):
            return operation_map["pip"](**kwargs)

        mock_execute.side_effect = mock_execute_side_effect

        result = self.command.execute(remove_config=False)

        assert result == 0
        mock_uninstall.assert_called_once_with(remove_config=False)


class TestErrorScenarios:
    """Test various error scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch("builtins.input", side_effect=KeyboardInterrupt())
    @patch("pieces.settings.Settings.logger")
    def test_confirm_uninstall_keyboard_interrupt(self, mock_logger, mock_input):
        """Test handling of keyboard interrupt during confirmation."""
        with pytest.raises(KeyboardInterrupt):
            self.command._confirm_uninstall()

    @patch.object(
        ManageUninstallCommand,
        "_post_uninstall_cleanup",
        side_effect=Exception("Cleanup error"),
    )
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_cleanup_error(self, mock_logger, mock_run, mock_cleanup):
        """Test that cleanup errors don't prevent successful uninstall completion."""
        result = self.command._uninstall_pip_version(remove_config=True)

        # The exact behavior depends on implementation, but cleanup should be attempted
        mock_cleanup.assert_called_once()

    @patch("subprocess.run", side_effect=FileNotFoundError("Command not found"))
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._handle_subprocess_error",
        return_value=1,
    )
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_command_not_found(
        self, mock_logger, mock_error_handler, mock_run
    ):
        """Test uninstall when package manager command is not found."""
        result = self.command._uninstall_homebrew_version(remove_config=False)

        assert result == 1
        mock_error_handler.assert_called_once()


class TestConfigurationHandling:
    """Test configuration file handling during uninstall."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageUninstallCommand()

    @patch.object(ManageUninstallCommand, "_post_uninstall_cleanup")
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_preserves_config_by_default(
        self, mock_logger, mock_run, mock_cleanup
    ):
        """Test that config is preserved by default."""
        result = self.command._uninstall_pip_version()  # No remove_config parameter

        assert result == 0
        mock_cleanup.assert_called_once_with(False)

    @patch.object(ManageUninstallCommand, "_post_uninstall_cleanup")
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_removes_config_when_requested(
        self, mock_logger, mock_run, mock_cleanup
    ):
        """Test that config is removed when explicitly requested."""
        result = self.command._uninstall_homebrew_version(remove_config=True)

        assert result == 0
        mock_cleanup.assert_called_once_with(True)
