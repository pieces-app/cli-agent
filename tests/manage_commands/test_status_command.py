"""
Tests for manage status command.
"""

import subprocess
from unittest.mock import Mock, patch, MagicMock

from pieces.command_interface.manage_commands.status_command import ManageStatusCommand
from pieces._vendor.pieces_os_client.models.updating_status_enum import (
    UpdatingStatusEnum,
)


class TestManageStatusCommand:
    """Test the ManageStatusCommand class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageStatusCommand()

    def test_command_properties(self):
        """Test command basic properties."""
        assert self.command.get_name() == "status"
        assert "Show Pieces CLI status" in self.command.get_help()
        assert len(self.command.get_examples()) > 0

    def test_add_arguments(self):
        """Test argument parsing setup."""
        parser = MagicMock()
        self.command.add_arguments(parser)
        # Status command has no additional arguments
        parser.add_argument.assert_not_called()


class TestVersionQueries:
    """Test version query methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageStatusCommand()

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
    def test_get_latest_chocolatey_version_error(self, mock_run):
        """Test Chocolatey version query error handling."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "choco")

        result = self.command._get_latest_chocolatey_version()
        assert result is None

    @patch("subprocess.run")
    def test_get_latest_chocolatey_version_not_found(self, mock_run):
        """Test when Chocolatey doesn't return expected format."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "other-package|4.5.6"  # No pieces-cli
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
    def test_get_latest_winget_version_error(self, mock_run):
        """Test WinGet version query error handling."""
        mock_run.side_effect = FileNotFoundError()

        result = self.command._get_latest_winget_version()
        assert result is None

    @patch("subprocess.run")
    def test_get_latest_winget_version_not_found(self, mock_run):
        """Test when WinGet doesn't return expected format."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Name  Id  Version\nOther App  SomeApp  1.0.0"
        mock_run.return_value = mock_result

        result = self.command._get_latest_winget_version()
        assert result is None

    @patch("subprocess.run")
    def test_get_latest_winget_version_invalid_format(self, mock_run):
        """Test WinGet with invalid format."""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "MeshIntelligentTechnologies.PiecesCLI invalid"
        mock_run.return_value = mock_result

        result = self.command._get_latest_winget_version()
        assert result is None


class TestExecuteCommand:
    """Test the main execute command functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageStatusCommand()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_execute_pip_installation_with_updates(
        self, mock_client, mock_logger, mock_version_checker, mock_pypi, mock_detect
    ):
        """Test status display for pip installation with updates available."""
        # Setup mocks
        mock_detect.return_value = "pip"
        mock_pypi.return_value = "1.2.0"
        mock_version_checker.return_value = True
        mock_client.is_pieces_running.return_value = False

        with patch("pieces.__version__", "1.0.0"):
            result = self.command.execute()

        assert result == 0
        mock_detect.assert_called_once()
        mock_pypi.assert_called_once()
        mock_version_checker.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_homebrew_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_execute_homebrew_installation_no_updates(
        self, mock_client, mock_logger, mock_version_checker, mock_homebrew, mock_detect
    ):
        """Test status display for Homebrew installation with no updates."""
        # Setup mocks
        mock_detect.return_value = "homebrew"
        mock_homebrew.return_value = "1.0.0"
        mock_version_checker.return_value = False
        mock_client.is_pieces_running.return_value = False

        with patch("pieces.__version__", "1.0.0"):
            result = self.command.execute()

        assert result == 0
        mock_homebrew.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_execute_installer_method(
        self, mock_client, mock_logger, mock_pypi, mock_detect
    ):
        """Test status display for installer script method."""
        mock_detect.return_value = "installer"
        mock_pypi.return_value = "1.2.0"
        mock_client.is_pieces_running.return_value = False

        with patch(
            "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker",
            return_value=True,
        ):
            result = self.command.execute()

        assert result == 0
        mock_pypi.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch.object(ManageStatusCommand, "_get_latest_chocolatey_version")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_execute_chocolatey_method(
        self, mock_client, mock_logger, mock_choco, mock_detect
    ):
        """Test status display for Chocolatey method."""
        mock_detect.return_value = "chocolatey"
        mock_choco.return_value = "1.2.0"
        mock_client.is_pieces_running.return_value = False

        with patch(
            "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker",
            return_value=False,
        ):
            result = self.command.execute()

        assert result == 0
        mock_choco.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch.object(ManageStatusCommand, "_get_latest_winget_version")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_execute_winget_method(
        self, mock_client, mock_logger, mock_winget, mock_detect
    ):
        """Test status display for WinGet method."""
        mock_detect.return_value = "winget"
        mock_winget.return_value = "1.2.0"
        mock_client.is_pieces_running.return_value = False

        with patch(
            "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker",
            return_value=True,
        ):
            result = self.command.execute()

        assert result == 0
        mock_winget.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.print_installation_detection_help"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_execute_unknown_installation_shows_help(
        self, mock_client, mock_logger, mock_help, mock_pypi, mock_detect
    ):
        """Test that help is shown for unknown installation method."""
        mock_detect.return_value = "unknown"
        mock_pypi.return_value = "1.2.0"
        mock_client.is_pieces_running.return_value = False

        with patch(
            "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker",
            return_value=False,
        ):
            result = self.command.execute()

        assert result == 0
        mock_help.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_execute_unsupported_installation_type(
        self, mock_client, mock_logger, mock_pypi, mock_detect
    ):
        """Test status display for unsupported installation type."""
        mock_detect.return_value = "custom_method"
        mock_pypi.return_value = "1.2.0"
        mock_client.is_pieces_running.return_value = False

        with patch(
            "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker",
            return_value=True,
        ):
            result = self.command.execute()

        assert result == 0
        mock_pypi.assert_called_once()  # Should fallback to PyPI

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_execute_version_fetch_failed(
        self, mock_client, mock_logger, mock_pypi, mock_detect
    ):
        """Test status display when version fetching fails."""
        mock_detect.return_value = "pip"
        mock_pypi.return_value = None  # Version fetch failed
        mock_client.is_pieces_running.return_value = False

        result = self.command.execute()

        assert result == 0  # Should still succeed but show warning

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    @patch("pieces.settings.Settings.startup")
    def test_execute_with_pieces_os_running(
        self,
        mock_startup,
        mock_client,
        mock_logger,
        mock_version_checker,
        mock_pypi,
        mock_detect,
    ):
        """Test status display when Pieces OS is running."""
        # Setup mocks for Pieces OS status
        mock_detect.return_value = "pip"
        mock_pypi.return_value = "1.2.0"
        mock_version_checker.return_value = False
        mock_client.is_pieces_running.return_value = True

        # Mock OS API for update check
        mock_os_api = Mock()
        mock_update_result = Mock()
        mock_update_result.status = UpdatingStatusEnum.UP_TO_DATE
        mock_os_api.os_update_check.return_value = mock_update_result
        mock_client.os_api = mock_os_api

        with patch("pieces.settings.Settings", pieces_os_version="2.0.0"):
            result = self.command.execute()

        assert result == 0
        mock_startup.assert_called_once()
        mock_os_api.os_update_check.assert_called_once()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_execute_pieces_os_not_running(
        self, mock_client, mock_logger, mock_pypi, mock_detect
    ):
        """Test status display when Pieces OS is not running."""
        mock_detect.return_value = "pip"
        mock_pypi.return_value = "1.2.0"
        mock_client.is_pieces_running.return_value = False

        with patch(
            "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker",
            return_value=False,
        ):
            result = self.command.execute()

        assert result == 0
        # Should not try to startup or check OS updates
        mock_client.os_api.os_update_check.assert_not_called() if hasattr(
            mock_client, "os_api"
        ) else None


class TestPiecesOSStatusHandling:
    """Test Pieces OS status handling functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageStatusCommand()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    @patch("pieces.settings.Settings.startup")
    @patch("pieces.core.update_pieces_os.PiecesUpdater.get_status_message")
    def test_different_os_update_statuses(
        self,
        mock_status_msg,
        mock_startup,
        mock_client,
        mock_logger,
        mock_version_checker,
        mock_pypi,
        mock_detect,
    ):
        """Test handling of different Pieces OS update statuses."""
        # Setup basic mocks
        mock_detect.return_value = "pip"
        mock_pypi.return_value = "1.0.0"
        mock_version_checker.return_value = False
        mock_client.is_pieces_running.return_value = True
        mock_status_msg.return_value = "Up to date"

        # Test different status values
        test_statuses = [
            UpdatingStatusEnum.UP_TO_DATE,
            UpdatingStatusEnum.DOWNLOADING,
            UpdatingStatusEnum.AVAILABLE,
            UpdatingStatusEnum.READY_TO_RESTART,
            UpdatingStatusEnum.CONTACT_SUPPORT,
            UpdatingStatusEnum.REINSTALL_REQUIRED,
            UpdatingStatusEnum.UNKNOWN,
        ]

        for status in test_statuses:
            # Reset mocks
            mock_startup.reset_mock()

            # Mock OS API
            mock_os_api = Mock()
            mock_update_result = Mock()
            mock_update_result.status = status
            mock_os_api.os_update_check.return_value = mock_update_result
            mock_client.os_api = mock_os_api

            with patch("pieces.settings.Settings", pieces_os_version="2.0.0"):
                result = self.command.execute()

            assert result == 0
            mock_startup.assert_called_once()


class TestErrorHandling:
    """Test error handling scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageStatusCommand()

    @patch("subprocess.run")
    def test_chocolatey_subprocess_error_handling(self, mock_run):
        """Test error handling in Chocolatey version checking."""
        mock_run.side_effect = FileNotFoundError("choco not found")

        result = self.command._get_latest_chocolatey_version()
        assert result is None

    @patch("subprocess.run")
    def test_winget_subprocess_error_handling(self, mock_run):
        """Test error handling in WinGet version checking."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "winget")

        result = self.command._get_latest_winget_version()
        assert result is None

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_version_checker_error_handling(
        self, mock_client, mock_logger, mock_pypi, mock_detect
    ):
        """Test error handling when version checker fails."""
        mock_detect.return_value = "pip"
        mock_pypi.return_value = "1.2.0"
        mock_client.is_pieces_running.return_value = False

        with patch(
            "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker",
            side_effect=Exception("Version check error"),
        ):
            # Should not crash, should handle gracefully
            result = self.command.execute()
            assert result == 0


class TestDisplayFormatting:
    """Test display formatting and output."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command = ManageStatusCommand()

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_output_formatting_with_updates(
        self, mock_client, mock_logger, mock_version_checker, mock_pypi, mock_detect
    ):
        """Test that output is properly formatted when updates are available."""
        mock_detect.return_value = "pip"
        mock_pypi.return_value = "1.2.0"
        mock_version_checker.return_value = True
        mock_client.is_pieces_running.return_value = False

        with patch("pieces.__version__", "1.0.0"):
            result = self.command.execute()

        assert result == 0
        # Verify logger was called with expected formatting
        assert mock_logger.print.called

    @patch(
        "pieces.command_interface.manage_commands.status_command.detect_installation_type"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker"
    )
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_output_formatting_no_updates(
        self, mock_client, mock_logger, mock_version_checker, mock_pypi, mock_detect
    ):
        """Test that output is properly formatted when no updates are available."""
        mock_detect.return_value = "homebrew"
        mock_pypi.return_value = "1.0.0"
        mock_version_checker.return_value = False
        mock_client.is_pieces_running.return_value = False

        with patch(
            "pieces.command_interface.manage_commands.status_command.get_latest_homebrew_version",
            return_value="1.0.0",
        ):
            with patch("pieces.__version__", "1.0.0"):
                result = self.command.execute()

        assert result == 0
        assert mock_logger.print.called

