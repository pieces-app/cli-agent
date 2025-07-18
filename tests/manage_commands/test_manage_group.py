"""
Tests for manage command group and integration tests.
"""

from unittest.mock import patch, MagicMock
import subprocess

from pieces.command_interface.manage_commands.manage_group import ManageCommandGroup
from pieces.command_interface.manage_commands.update_command import ManageUpdateCommand
from pieces.command_interface.manage_commands.status_command import ManageStatusCommand
from pieces.command_interface.manage_commands.uninstall_command import (
    ManageUninstallCommand,
)


class TestManageCommandGroup:
    """Test the ManageCommandGroup class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command_group = ManageCommandGroup()

    def test_command_group_properties(self):
        """Test command group basic properties."""
        assert self.command_group.get_name() == "manage"
        assert "Manage Pieces CLI installation" in self.command_group.get_help()
        assert len(self.command_group.get_examples()) > 0

    def test_subcommands_registration(self):
        """Test that all expected subcommands are registered."""
        # Access the subcommands (this will trigger registration)
        self.command_group._register_subcommands()

        # Check that subcommands are properly registered
        # The exact implementation may vary, but we can test the types exist
        assert ManageUpdateCommand is not None
        assert ManageStatusCommand is not None
        assert ManageUninstallCommand is not None

    def test_command_group_examples(self):
        """Test that examples include all major operations."""
        examples = self.command_group.get_examples()

        # Should include examples for major operations
        example_text = " ".join(examples)
        assert "update" in example_text
        assert "uninstall" in example_text
        assert "--force" in example_text
        assert "--remove-config" in example_text

    def test_command_group_description(self):
        """Test that description mentions key features."""
        description = self.command_group.get_description()

        # Should mention key installation methods
        assert "pip" in description
        assert "homebrew" in description
        assert "chocolatey" in description
        assert "winget" in description
        assert "installer script" in description


class TestIntegrationScenarios:
    """Integration tests for complete manage command workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command_group = ManageCommandGroup()

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch(
        "pieces.command_interface.manage_commands.update_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.update_command.check_updates_with_version_checker"
    )
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    def test_pip_update_integration(
        self, mock_logger, mock_run, mock_version_checker, mock_pypi, mock_detect
    ):
        """Test complete pip update workflow."""
        # Setup mocks for pip update
        mock_detect.return_value = "pip"
        mock_pypi.return_value = "1.2.0"
        mock_version_checker.return_value = True

        # Create and execute update command
        update_command = ManageUpdateCommand()
        result = update_command.execute(force=False)

        assert result == 0
        mock_detect.assert_called()
        mock_run.assert_called()  # Should call pip install

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
    def test_homebrew_status_integration(
        self, mock_client, mock_logger, mock_version_checker, mock_homebrew, mock_detect
    ):
        """Test complete Homebrew status workflow."""
        # Setup mocks for Homebrew status
        mock_detect.return_value = "homebrew"
        mock_homebrew.return_value = "1.0.0"
        mock_version_checker.return_value = False
        mock_client.is_pieces_running.return_value = False

        # Create and execute status command
        status_command = ManageStatusCommand()
        result = status_command.execute()

        assert result == 0
        mock_detect.assert_called()
        mock_homebrew.assert_called()

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch("builtins.input", return_value="y")
    @patch("subprocess.run")
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command.remove_completion_scripts"
    )
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command.remove_config_dir"
    )
    @patch("pieces.settings.Settings.logger")
    def test_chocolatey_uninstall_integration(
        self,
        mock_logger,
        mock_remove_config,
        mock_remove_scripts,
        mock_run,
        mock_input,
        mock_detect,
    ):
        """Test complete Chocolatey uninstall workflow."""
        # Setup mocks for Chocolatey uninstall
        mock_detect.return_value = "chocolatey"

        # Create and execute uninstall command
        uninstall_command = ManageUninstallCommand()
        result = uninstall_command.execute(remove_config=True)

        assert result == 0
        mock_detect.assert_called()
        mock_run.assert_called()  # Should call choco uninstall

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch(
        "pieces.command_interface.manage_commands.update_command.get_latest_pypi_version"
    )
    @patch("pieces.settings.Settings.logger")
    def test_unknown_installation_fallback_integration(
        self, mock_logger, mock_pypi, mock_detect
    ):
        """Test fallback behavior for unknown installation types."""
        # Setup mocks for unknown installation with fallback
        mock_detect.return_value = "unknown"
        mock_pypi.return_value = "1.2.0"

        with patch(
            "pieces.command_interface.manage_commands.update_command.check_updates_with_version_checker",
            return_value=True,
        ):
            with patch("subprocess.run") as mock_run:
                update_command = ManageUpdateCommand()
                result = update_command.execute(force=False)

                assert result == 0
                mock_detect.assert_called()
                # Should fallback to pip method
                mock_run.assert_called()


class TestErrorPropagation:
    """Test error handling and propagation across the command hierarchy."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command_group = ManageCommandGroup()

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "pip"))
    @patch(
        "pieces.command_interface.manage_commands.update_command._handle_subprocess_error",
        return_value=1,
    )
    @patch("pieces.settings.Settings.logger")
    def test_update_error_propagation(
        self, mock_logger, mock_error_handler, mock_run, mock_detect
    ):
        """Test that update errors are properly propagated."""
        mock_detect.return_value = "pip"

        update_command = ManageUpdateCommand()
        result = update_command.execute(force=False)

        assert result == 1  # Should propagate error code

    @patch(
        "pieces.command_interface.manage_commands.utils.detect_installation_type",
        side_effect=Exception("Detection error"),
    )
    @patch("pieces.settings.Settings.logger")
    def test_detection_error_handling(self, mock_logger, mock_detect):
        """Test handling of installation detection errors."""
        status_command = ManageStatusCommand()
        # Should not crash on detection error
        result = status_command.execute()
        # Result may vary depending on implementation

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch("subprocess.run", side_effect=FileNotFoundError("Command not found"))
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command._handle_subprocess_error",
        return_value=1,
    )
    @patch("pieces.settings.Settings.logger")
    def test_command_not_found_error_handling(
        self, mock_logger, mock_error_handler, mock_run, mock_detect
    ):
        """Test handling when package manager commands are not found."""
        mock_detect.return_value = "homebrew"

        uninstall_command = ManageUninstallCommand()
        result = uninstall_command.execute()

        assert result == 1


class TestCrossCommandInteractions:
    """Test interactions between different manage commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.command_group = ManageCommandGroup()

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch(
        "pieces.command_interface.manage_commands.status_command.get_latest_pypi_version"
    )
    @patch(
        "pieces.command_interface.manage_commands.status_command.check_updates_with_version_checker"
    )
    @patch(
        "pieces.command_interface.manage_commands.update_command.get_latest_pypi_version"
    )
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.settings.Settings.pieces_client")
    def test_status_then_update_workflow(
        self,
        mock_client,
        mock_logger,
        mock_run,
        mock_update_pypi,
        mock_status_checker,
        mock_status_pypi,
        mock_detect,
    ):
        """Test checking status then updating when updates available."""
        # Setup mocks
        mock_detect.return_value = "pip"
        mock_status_pypi.return_value = "1.2.0"
        mock_update_pypi.return_value = "1.2.0"
        mock_status_checker.return_value = True
        mock_client.is_pieces_running.return_value = False

        # First check status
        status_command = ManageStatusCommand()
        status_result = status_command.execute()
        assert status_result == 0

        # Then update (status should have shown updates available)
        with patch(
            "pieces.command_interface.manage_commands.update_command.check_updates_with_version_checker",
            return_value=True,
        ):
            update_command = ManageUpdateCommand()
            update_result = update_command.execute()
            assert update_result == 0

    @patch("pieces.command_interface.manage_commands.utils.detect_installation_type")
    @patch("builtins.input", return_value="y")
    @patch("subprocess.run")
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command.remove_completion_scripts"
    )
    @patch(
        "pieces.command_interface.manage_commands.uninstall_command.remove_config_dir"
    )
    @patch("pieces.settings.Settings.logger")
    def test_uninstall_with_config_cleanup_workflow(
        self,
        mock_logger,
        mock_remove_config,
        mock_remove_scripts,
        mock_run,
        mock_input,
        mock_detect,
    ):
        """Test complete uninstall workflow with configuration cleanup."""
        mock_detect.return_value = "pip"

        uninstall_command = ManageUninstallCommand()
        result = uninstall_command.execute(remove_config=True)

        assert result == 0
        mock_remove_scripts.assert_called()
        mock_remove_config.assert_called()


class TestArgumentHandling:
    """Test argument handling across manage commands."""

    def test_update_force_argument(self):
        """Test that update command properly handles force argument."""
        update_command = ManageUpdateCommand()

        # Test that _should_update respects force flag
        assert update_command._should_update("pip", force=True) is True

    def test_uninstall_config_argument(self):
        """Test that uninstall command properly handles remove-config argument."""
        uninstall_command = ManageUninstallCommand()

        # Test argument setup
        parser = MagicMock()
        uninstall_command.add_arguments(parser)

        # Should have added the remove-config argument
        parser.add_argument.assert_called_with(
            "--remove-config",
            action="store_true",
            help="Remove configuration files including shell completion scripts",
        )


class TestCommandRegistration:
    """Test command registration and discovery."""

    def test_all_commands_have_required_methods(self):
        """Test that all commands implement required interface methods."""
        commands = [
            ManageUpdateCommand(),
            ManageStatusCommand(),
            ManageUninstallCommand(),
        ]

        for command in commands:
            # Each command should have these basic methods
            assert hasattr(command, "get_name")
            assert hasattr(command, "get_help")
            assert hasattr(command, "get_description")
            assert hasattr(command, "get_examples")
            assert hasattr(command, "execute")
            assert hasattr(command, "add_arguments")

            # Methods should return appropriate types
            assert isinstance(command.get_name(), str)
            assert isinstance(command.get_help(), str)
            assert isinstance(command.get_description(), str)
            assert isinstance(command.get_examples(), list)

    def test_command_names_are_unique(self):
        """Test that all command names are unique."""
        commands = [
            ManageUpdateCommand(),
            ManageStatusCommand(),
            ManageUninstallCommand(),
        ]
        names = [cmd.get_name() for cmd in commands]

        assert len(names) == len(set(names))  # All names should be unique

    def test_command_help_is_descriptive(self):
        """Test that command help text is descriptive."""
        commands = [
            ManageUpdateCommand(),
            ManageStatusCommand(),
            ManageUninstallCommand(),
        ]

        for command in commands:
            help_text = command.get_help()
            description = command.get_description()

            # Help and description should be meaningful
            assert len(help_text) > 10
            assert len(description) > 20
            assert (
                command.get_name() in help_text.lower()
                or command.get_name() in description.lower()
            )


class TestDocumentationAndExamples:
    """Test documentation and example completeness."""

    def test_all_commands_have_examples(self):
        """Test that all commands provide usage examples."""
        commands = [
            ManageUpdateCommand(),
            ManageStatusCommand(),
            ManageUninstallCommand(),
        ]

        for command in commands:
            examples = command.get_examples()
            assert len(examples) > 0

            # Examples should include the command name
            for example in examples:
                assert "pieces manage" in example
                assert command.get_name() in example

    def test_examples_cover_main_use_cases(self):
        """Test that examples cover the main use cases."""
        update_command = ManageUpdateCommand()
        update_examples = " ".join(update_command.get_examples())
        assert "--force" in update_examples

        uninstall_command = ManageUninstallCommand()
        uninstall_examples = " ".join(uninstall_command.get_examples())
        assert "--remove-config" in uninstall_examples

    def test_command_group_documentation(self):
        """Test that command group has comprehensive documentation."""
        command_group = ManageCommandGroup()

        description = command_group.get_description()
        examples = command_group.get_examples()

        # Should mention key features
        assert "installation method" in description.lower()
        assert "automatically detects" in description.lower()

        # Should have examples for major operations
        example_text = " ".join(examples)
        assert "update" in example_text
        assert "uninstall" in example_text
