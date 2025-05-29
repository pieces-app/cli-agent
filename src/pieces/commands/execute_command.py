import os
import shlex
import sys
from typing import TYPE_CHECKING, Dict, Iterable, Optional
import json
from pieces.settings import Settings
from .assets_command import AssetsCommands, check_asset_selected, check_assets_existence
from pathlib import Path
import subprocess

if TYPE_CHECKING:
    from pieces.wrapper.basic_identifier.asset import BasicAsset


class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


class ExecuteCommand:
    @classmethod
    def handle_execute(cls, **kwargs):
        # parse the args manually for better performance
        passed_args = set()
        for i, arg in enumerate(sys.argv[1:]):
            if arg.startswith("--"):
                passed_args.add(arg.lstrip("--").split("=")[0] + "_handler")

        if passed_args:
            cls.save_commands_map(passed_args, kwargs)
            return
        cls.execute_command(**kwargs)

    @classmethod
    @check_asset_selected
    @check_assets_existence
    def execute_command(cls, asset: Optional["BasicAsset"], **kwargs):
        if not asset:
            return
        try:
            if not asset.raw_content:
                return Settings.show_error("Couldn't get the material content")
            if not asset.classification:
                return Settings.show_error(
                    "Couldn't extract the material classification"
                )
            map = cls.get_command_map()
            if asset.classification.value not in map:
                return Settings.show_error(
                    f"No matching command found for material type: '{asset.classification.value}'.",
                    f"Tip: Use `pieces execute --{asset.classification.value}` to configure a handler for this material type.",
                )
            file = AssetsCommands.create_asset_file(asset)
            file_no_extension = Path(file).with_suffix("")
            commands = (
                map[asset.classification.value]
                .format_map(
                    SafeDict(
                        {
                            "content": asset.raw_content,
                            "file": file,
                            "file_no_extension": file_no_extension,
                        }
                    )
                )
                .split("&&")
            )
            stderr = ""
            stdout = ""
            for command in commands:
                out = shlex.split(command)
                result = subprocess.run(
                    out,
                    capture_output=True,
                    text=True,
                )
                stdout += result.stdout
                if result.stderr:
                    stderr += result.stderr
            Settings.logger.print(f"Executing {asset.classification.value} command:")
            Settings.logger.print(stdout)
            if stderr:
                Settings.logger.print("Errors:")
                Settings.logger.print(stderr)
        except subprocess.CalledProcessError as e:
            Settings.logger.print(f"Error executing command: {e}")
        except Exception as e:
            Settings.logger.print(f"An error occurred: {e}")

    @staticmethod
    def get_command_map() -> Dict[str, str]:
        commands_map: dict = {}
        if os.path.exists(Settings.execute_command_extensions_map):
            with open(Settings.execute_command_extensions_map, "r") as f:
                commands_map = json.load(f)

        commands_map.setdefault("py", "python '{file}'")
        commands_map.setdefault("bash", "bash -c {content}")
        commands_map.setdefault("sh", "sh -c {content}")
        commands_map.setdefault("js", "node -e {content}")
        commands_map.setdefault("ts", "ts-node -e {content}")
        commands_map.setdefault("rb", "ruby -e {content}")
        commands_map.setdefault("lua", "lua -e {content}")
        commands_map.setdefault("perl", "perl -e {content}")
        commands_map.setdefault("php", "php -r {content}")
        commands_map.setdefault("groovy", "groovy -e {content}")
        commands_map.setdefault("scala", "scala -e {content}")
        commands_map.setdefault(
            "rs", "rustc '{file}' -o '{file_no_extension}' && '{file_no_extension}'"
        )
        commands_map.setdefault("dart", "dart '{file}'")
        commands_map.setdefault(
            "c", "gcc '{file}' -o '{file_no_extension}' && '{file_no_extension}'"
        )
        commands_map.setdefault(
            "cpp", "g++ '{file}' -o '{file_no_extension}' && '{file_no_extension}'"
        )
        commands_map.setdefault("go", "go run '{file}'")
        return commands_map

    @classmethod
    def save_commands_map(cls, commands: Iterable[str], default: Dict[str, str]):
        data = cls.get_command_map()
        for command in commands:
            data[command.removesuffix("_handler")] = default[command]
        with open(Settings.execute_command_extensions_map, "w") as f:
            json.dump(data, f)
