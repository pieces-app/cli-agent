import argparse
import pytest
from unittest.mock import patch

from pieces.command_interface.config_command import ConfigCommand
from pieces.config.managers.cli import CLIManager
from pieces.settings import Settings


REAL_SETTINGS_STARTUP = Settings.startup.__func__


class TestConfigCommand:
    @pytest.fixture
    def config_command(self):
        return ConfigCommand()

    @patch.object(Settings, "logger")
    def test_execute_persists_auto_launch_pieces_os(
        self, mock_logger, config_command, tmp_path
    ):
        cli_config = CLIManager(tmp_path / "cli.json")

        with patch.object(Settings, "cli_config", cli_config):
            result = config_command.execute(auto_launch_pieces_os=False)

        assert result == 0
        reloaded_config = CLIManager(tmp_path / "cli.json")
        assert reloaded_config.auto_launch_pieces_os is False
        mock_logger.print.assert_called_once()
        assert "auto-launch" in mock_logger.print.call_args[0][0].lower()

    @patch.object(Settings, "logger")
    def test_execute_updates_editor_and_auto_launch_together(
        self, mock_logger, config_command, tmp_path
    ):
        cli_config = CLIManager(tmp_path / "cli.json")

        with patch.object(Settings, "cli_config", cli_config):
            result = config_command.execute(
                editor="vim", auto_launch_pieces_os=False
            )

        assert result == 0
        reloaded_config = CLIManager(tmp_path / "cli.json")
        assert reloaded_config.editor == "vim"
        assert reloaded_config.auto_launch_pieces_os is False
        assert mock_logger.print.call_count == 2

    def test_add_arguments_supports_no_auto_launch_flag(self, config_command):
        parser = argparse.ArgumentParser()
        config_command.add_arguments(parser)

        args = parser.parse_args(["--no-auto-launch-pieces-os"])

        assert args.auto_launch_pieces_os is False


class TestSettingsStartup:
    @patch("sys.exit", side_effect=SystemExit(2))
    @patch.object(Settings, "logger")
    @patch.object(Settings, "cli_config")
    @patch.object(Settings, "pieces_client")
    @patch.object(Settings, "open_pieces_widget")
    def test_startup_skips_launch_when_auto_launch_disabled(
        self,
        mock_open_pieces_widget,
        mock_pieces_client,
        mock_cli_config,
        mock_logger,
        mock_sys_exit,
    ):
        mock_cli_config.auto_launch_pieces_os = False
        mock_pieces_client.is_pieces_running.return_value = False
        mock_logger.confirm.return_value = False

        with pytest.raises(SystemExit):
            REAL_SETTINGS_STARTUP(Settings, bypass_login=False)

        mock_open_pieces_widget.assert_not_called()
        mock_logger.print.assert_called()
        assert "enable auto-launch" in mock_logger.print.call_args_list[-1][0][0].lower()
