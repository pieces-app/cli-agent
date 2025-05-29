import unittest
from unittest.mock import patch, Mock, call
from pieces.commands.assets_command import AssetsCommands
from pieces.commands.execute_command import ExecuteCommand
from pieces_os_client.models.classification_specific_enum import (
    ClassificationSpecificEnum,
)
import json
from pathlib import Path


class TestExecuteCommand(unittest.TestCase):
    def setUp(self):
        self.mock_asset = Mock()
        self.mock_asset.raw_content = "print('Hello, World!')"
        self.mock_asset.classification = ClassificationSpecificEnum.PY
        AssetsCommands.current_asset = self.mock_asset

    @patch("pieces.settings.Settings.pieces_client.assets", return_value=[Mock()])
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.commands.execute_command.AssetsCommands")
    def test_execute_python_command(
        self,
        mock_assets_command,
        mock_settings_logger,
        mock_subprocess_run,
        mock_assets,
    ):
        mock_subprocess_run.return_value.stdout = "Hello, World!"
        mock_subprocess_run.return_value.stderr = ""
        mock_assets_command.create_asset_file.return_value = "/tmp/test.py"
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        mock_assets_command.create_asset_file.assert_called_once_with(self.mock_asset)
        mock_subprocess_run.assert_called_once()
        mock_settings_logger.print.assert_has_calls(
            [call("Executing py command:"), call("Hello, World!")]
        )

    @patch("pieces.settings.Settings.pieces_client.assets", return_value=[Mock()])
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.commands.execute_command.AssetsCommands")
    def test_execute_command_with_error(
        self,
        mock_assets_command,
        mock_settings_logger,
        mock_subprocess_run,
        mock_assets,
    ):
        mock_subprocess_run.return_value.stdout = ""
        mock_subprocess_run.return_value.stderr = "Error: Invalid syntax"
        mock_assets_command.create_asset_file.return_value = "/tmp/test.py"
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        mock_settings_logger.print.assert_has_calls(
            [
                call("Executing py command:"),
                call(""),
                call("Errors:"),
                call("Error: Invalid syntax"),
            ]
        )

    @patch(
        "pieces.wrapper.basic_identifier.asset.BasicAsset.get_identifiers",
        return_value=[],
    )
    @patch(
        "pieces.wrapper.basic_identifier.asset.AssetSnapshot.pieces_client",
        new_callable=Mock,
    )
    @patch("pieces.settings.Settings.pieces_client", new_callable=Mock)
    @patch("pieces.settings.Settings.logger")
    def test_execute_command_no_asset(
        self,
        mock_settings_logger,
        mock_pieces_client,
        mock_asset_snapshot_client,
        mock_get_identifiers,
    ):
        AssetsCommands.current_asset = None
        with patch(
            "prompt_toolkit.application.Application.run", side_effect=EOFError
        ) as mock_prompt:
            try:
                ExecuteCommand.execute_command()
            except EOFError:
                pass
            mock_prompt.assert_called_once()

    @patch("pieces.settings.Settings.show_error")
    @patch("pieces.settings.Settings.pieces_client", new_callable=Mock)
    @patch("pieces.settings.Settings.logger")
    def test_execute_command_no_content(
        self, mock_settings_logger, mock_pieces_client, mock_show_error
    ):
        self.mock_asset.raw_content = None
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        mock_show_error.assert_called_with("Couldn't get the material content")

    @patch("pieces.settings.Settings.show_error")
    @patch("pieces.settings.Settings.pieces_client", new_callable=Mock)
    @patch("pieces.settings.Settings.logger")
    def test_execute_command_no_classification(
        self, mock_settings_logger, mock_pieces_client, mock_show_error
    ):
        self.mock_asset.classification = None
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        mock_show_error.assert_called_with(
            "Couldn't extract the material classification"
        )

    @patch("pieces.settings.Settings.show_error")
    @patch("pieces.settings.Settings.pieces_client", new_callable=Mock)
    @patch("pieces.settings.Settings.logger")
    def test_execute_command_unsupported_type(
        self, mock_settings_logger, mock_pieces_client, mock_show_error
    ):
        self.mock_asset.classification = ClassificationSpecificEnum.ABAP
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        mock_show_error.assert_called_with(
            "No matching command found for material type: 'abap'.",
            "Tip: Use `pieces execute --abap` to configure a handler for this material type.",
        )

    def test_save_commands_map(self):
        test_map = {"test_type_handler": "test_command {content}"}
        with patch(
            "pieces.settings.Settings.execute_command_extensions_map",
            new_callable=unittest.mock.PropertyMock,
        ) as mock_map:
            mock_map.return_value = str(Path("/tmp/test_map.json"))
            ExecuteCommand.save_commands_map(["test_type_handler"], test_map)
            with open(mock_map.return_value, "r") as f:
                saved_map = json.load(f)
            self.assertEqual(saved_map["test_type"], "test_command {content}")

    def test_get_command_map_defaults(self):
        command_map = ExecuteCommand.get_command_map()
        self.assertIn("py", command_map)
        self.assertIn("js", command_map)
        self.assertIn("bash", command_map)
        self.assertEqual(command_map["py"], "python '{file}'")
        self.assertEqual(command_map["js"], "node -e {content}")

    @patch("pieces.settings.Settings.pieces_client.assets", return_value=[Mock()])
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.commands.execute_command.AssetsCommands")
    def test_execute_javascript_command(
        self,
        mock_assets_command,
        mock_settings_logger,
        mock_subprocess_run,
        mock_assets,
    ):
        self.mock_asset.classification = ClassificationSpecificEnum.JS
        self.mock_asset.raw_content = "console.log('Hello from JS!')"
        mock_subprocess_run.return_value.stdout = "Hello from JS!"
        mock_subprocess_run.return_value.stderr = ""
        mock_assets_command.create_asset_file.return_value = "/tmp/test.js"
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        mock_subprocess_run.assert_called_once()
        mock_settings_logger.print.assert_any_call("Executing js command:")
        mock_settings_logger.print.assert_any_call("Hello from JS!")

    @patch("pieces.settings.Settings.pieces_client.assets", return_value=[Mock()])
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.commands.execute_command.AssetsCommands")
    def test_execute_lua_command(
        self,
        mock_assets_command,
        mock_settings_logger,
        mock_subprocess_run,
        mock_assets,
    ):
        self.mock_asset.classification = ClassificationSpecificEnum.LUA
        self.mock_asset.raw_content = "print('Hello from Lua!')"
        mock_subprocess_run.return_value.stdout = "Hello from Lua!"
        mock_subprocess_run.return_value.stderr = ""
        mock_assets_command.create_asset_file.return_value = "/tmp/test.lua"
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        mock_subprocess_run.assert_called_once()
        mock_settings_logger.print.assert_any_call("Executing lua command:")
        mock_settings_logger.print.assert_any_call("Hello from Lua!")

    @patch("pieces.settings.Settings.pieces_client.assets", return_value=[Mock()])
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.commands.execute_command.AssetsCommands")
    def test_execute_rust_command(
        self,
        mock_assets_command,
        mock_settings_logger,
        mock_subprocess_run,
        mock_assets,
    ):
        self.mock_asset.classification = ClassificationSpecificEnum.RS
        self.mock_asset.raw_content = 'fn main() { println!("Hello from Rust!"); }'
        mock_subprocess_run.return_value.stdout = "Hello from Rust!"
        mock_subprocess_run.return_value.stderr = ""
        mock_assets_command.create_asset_file.return_value = "/tmp/test.rs"
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        # Should call twice: rustc and then the binary
        self.assertEqual(mock_subprocess_run.call_count, 2)
        mock_settings_logger.print.assert_any_call("Executing rs command:")

    @patch("pieces.settings.Settings.pieces_client.assets", return_value=[Mock()])
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.commands.execute_command.AssetsCommands")
    def test_execute_c_command(
        self,
        mock_assets_command,
        mock_settings_logger,
        mock_subprocess_run,
        mock_assets,
    ):
        self.mock_asset.classification = ClassificationSpecificEnum.C
        self.mock_asset.raw_content = (
            '#include <stdio.h>\nint main() { printf("Hello from C!\\n"); return 0; }'
        )
        mock_subprocess_run.return_value.stdout = "Hello from C!"
        mock_subprocess_run.return_value.stderr = ""
        mock_assets_command.create_asset_file.return_value = "/tmp/test.c"
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        # Should call twice: gcc and then the binary
        self.assertEqual(mock_subprocess_run.call_count, 2)
        mock_settings_logger.print.assert_any_call("Executing c command:")

    @patch("pieces.settings.Settings.pieces_client.assets", return_value=[Mock()])
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.commands.execute_command.AssetsCommands")
    def test_execute_cpp_command(
        self,
        mock_assets_command,
        mock_settings_logger,
        mock_subprocess_run,
        mock_assets,
    ):
        self.mock_asset.classification = ClassificationSpecificEnum.CPP
        self.mock_asset.raw_content = '#include <iostream>\nint main() { std::cout << "Hello from C++!" << std::endl; return 0; }'
        mock_subprocess_run.return_value.stdout = "Hello from C++!"
        mock_subprocess_run.return_value.stderr = ""
        mock_assets_command.create_asset_file.return_value = "/tmp/test.cpp"
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        # Should call twice: g++ and then the binary
        self.assertEqual(mock_subprocess_run.call_count, 2)
        mock_settings_logger.print.assert_any_call("Executing cpp command:")

    @patch("pieces.settings.Settings.pieces_client.assets", return_value=[Mock()])
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.commands.execute_command.AssetsCommands")
    def test_execute_go_command(
        self,
        mock_assets_command,
        mock_settings_logger,
        mock_subprocess_run,
        mock_assets,
    ):
        self.mock_asset.classification = ClassificationSpecificEnum.GO
        self.mock_asset.raw_content = (
            'package main\nimport "fmt"\nfunc main() { fmt.Println("Hello from Go!") }'
        )
        mock_subprocess_run.return_value.stdout = "Hello from Go!"
        mock_subprocess_run.return_value.stderr = ""
        mock_assets_command.create_asset_file.return_value = "/tmp/test.go"
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        mock_subprocess_run.assert_called_once_with(
            ["go", "run", "/tmp/test.go"], capture_output=True, text=True
        )
        mock_settings_logger.print.assert_any_call("Executing go command:")
        mock_settings_logger.print.assert_any_call("Hello from Go!")

    @patch("pieces.settings.Settings.pieces_client.assets", return_value=[Mock()])
    @patch("subprocess.run")
    @patch("pieces.settings.Settings.logger")
    @patch("pieces.commands.execute_command.AssetsCommands")
    def test_execute_bash_command(
        self,
        mock_assets_command,
        mock_settings_logger,
        mock_subprocess_run,
        mock_assets,
    ):
        self.mock_asset.classification = ClassificationSpecificEnum.BASH
        self.mock_asset.raw_content = "echo 'Hello from Bash!'"
        mock_subprocess_run.return_value.stdout = "Hello from Bash!"
        mock_subprocess_run.return_value.stderr = ""
        mock_assets_command.create_asset_file.return_value = "/tmp/test.sh"
        AssetsCommands.current_asset = self.mock_asset
        ExecuteCommand.execute_command()
        mock_subprocess_run.assert_called_once()
        mock_settings_logger.print.assert_any_call("Executing bash command:")
        mock_settings_logger.print.assert_any_call("Hello from Bash!")


if __name__ == "__main__":
    unittest.main()
