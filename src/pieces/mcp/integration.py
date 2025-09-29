import json
import os
from typing import Callable, Dict, List, Tuple, Optional
import sysconfig
import shutil
from rich.markdown import Markdown
import yaml
import sys

from pieces.copilot.ltm import check_ltm
from pieces.headless.exceptions import HeadlessError
from pieces.settings import Settings

from .utils import get_mcp_latest_url, get_mcp_urls
from ..utils import PiecesSelectMenu
from pieces.config.schemas.mcp import IntegrationDict, mcp_types, mcp_integration_types


class MCPProperties:
    pieces_cli_bin_path: Optional[str] = None

    def __init__(
        self,
        stdio_property: Dict,
        stdio_path: List,
        sse_property: Dict,
        sse_path: List,
        url_property_name: str = "url",
        command_property_name: str = "command",
        args_property_name: str = "args",
    ) -> None:
        self.stdio_property = stdio_property
        self.stdio_path = stdio_path
        self.sse_property = sse_property
        self.sse_path = sse_path
        self.url_property_name = url_property_name
        self.command_property_name = command_property_name
        self.args_property_name = args_property_name
        if not MCPProperties.pieces_cli_bin_path:
            MCPProperties.pieces_cli_bin_path = self.get_cli_wrapper()

    def get_cli_wrapper(self):
        wrapper_path = shutil.which("pieces")
        if wrapper_path:
            return wrapper_path
        scripts_dir = sysconfig.get_path("scripts")
        wrapper = os.path.join(scripts_dir, "pieces")
        if os.name == "nt":
            wrapper += ".exe"
        if os.path.exists(wrapper):
            return wrapper
        return os.path.abspath(sys.argv[0])

    def mcp_settings(self, mcp_type: mcp_types):
        if mcp_type == "sse":
            return self.sse_property
        else:
            return self.stdio_property

    def mcp_path(self, mcp_type: mcp_types):
        if mcp_type == "sse":
            return self.sse_path
        else:
            return self.stdio_path

    def mcp_modified_settings(self, mcp_type: mcp_types):
        mcp_settings = self.mcp_settings(mcp_type)
        if mcp_type == "sse":
            mcp_settings[self.url_property_name] = get_mcp_latest_url()
        else:
            mcp_settings[self.command_property_name] = self.pieces_cli_bin_path
            mcp_settings[self.args_property_name] = [
                "--ignore-onboarding",
                "mcp",
                "start",
            ]
        return mcp_settings


class Integration:
    def __init__(
        self,
        options: List[Tuple],
        text_success: str,
        readable: str,
        docs: str,
        get_settings_path: Callable,
        mcp_properties: MCPProperties,
        id: mcp_integration_types,
        error_text: Optional[str] = None,
        loader=json.load,
        saver=lambda x, y: json.dump(x, y, indent=4),
        support_sse: bool = True,
        check_existence_paths: Optional[List[str]] = None,
        check_existence_command: Optional[str] = None,
    ) -> None:
        # remove the css selector
        self.docs_no_css_selector = docs.split("#")[0]
        self.options = options
        self.text_end = text_success
        self.readable = readable
        self.error_text = error_text or (
            "Something went wrong. "
            f"Please refer to the documentation: `{self.docs_no_css_selector}`"
        )
        self.support_sse = support_sse
        self.docs = docs
        self.get_settings_path = get_settings_path
        self.loader = loader
        self.saver = saver
        self.id: str = id or self.readable.lower().replace(" ", "_")
        self._local_config = None
        self.mcp_properties = mcp_properties
        self.mcp_types: List[mcp_types] = ["sse", "stdio"]
        self.check_existence_paths = check_existence_paths or [
            os.path.dirname(self.get_settings_path())
        ]
        self.check_existence_command = check_existence_command

    def handle_options(self, stdio: bool, **kwargs):
        mcp_type = "stdio" if stdio else "sse"
        for option in range(len(self.options)):
            self.options[option][1]["mcp_type"] = mcp_type

        if self.options and not kwargs:
            return PiecesSelectMenu(self.options, self.on_select).run()
        else:
            return self.on_select(mcp_type, **kwargs)

    def run(self, stdio: bool, **kwargs) -> bool:
        if not stdio and not self.support_sse:
            Settings.logger.print(
                "[yellow]Warning: Using stdio instead of sse because sse connection is not supported"
            )
            stdio = True

        if not self.exists() and not Settings.logger.confirm(
            "This integration is not installed are you sure you want to proceed?",
            _default=True,
        ):
            return False

        if stdio and not self.mcp_properties.pieces_cli_bin_path:
            raise ValueError(
                "Pieces Cli is not added to the path you can't setup the stdio servers please add it to the path"
            )
        Settings.logger.print(
            f"Attempting to update Global {self.readable} MCP Tooling"
        )
        if not self.check_ltm():
            return False
        try:
            if not self.handle_options(stdio, **kwargs):
                return False
            Settings.logger.print(
                Markdown(f"✅ Pieces MCP is now enabled for {self.readable}!")
            )
            Settings.logger.print(
                Markdown(
                    f"For more information please refer to the docs: `{self.docs}`"
                )
            )
            Settings.logger.print(Markdown(self.text_end))
            return True
        except KeyboardInterrupt:
            return False
        except HeadlessError as e:
            raise e
        except Exception as e:  # noqa: E722
            Settings.logger.print(e)
            Settings.logger.critical(e)
            Settings.logger.print(Markdown(self.error_text))
            return False

    def check_ltm(self) -> bool:
        css_selector = "#installing-piecesos--configuring-permissions"
        return check_ltm(self.docs_no_css_selector + css_selector)

    def repair(self):
        paths_to_repair = self.need_repair()
        if paths_to_repair:
            [self.on_select(mcp_type, p) for p, mcp_type in paths_to_repair.items()]
        else:
            Settings.logger.print(f"No issues detected in {self.readable}")

    def on_select(self, mcp_type: mcp_types, path=None, **kwargs) -> bool:
        mcp_settings = self.mcp_properties.mcp_modified_settings(mcp_type)
        mcp_path = self.mcp_properties.mcp_path(mcp_type)
        if not path:
            path = self.get_settings_path(**kwargs)
        old_mcp_type = Settings.mcp_config.get_projects(self.id).get(path, mcp_type)
        if (
            (
                old_mcp_type != mcp_type and self.search(path, old_mcp_type)[0]
            )  # the old set up and NOT removed
            and not Settings.logger.confirm(
                f"{mcp_type} is already used as your {self.readable} MCP\n"
                f"Do you want to replace the {old_mcp_type} mcp with the {mcp_type} mcp?",
                _default=True,
            )
        ):
            return False
        dirname = os.path.dirname(path)
        try:
            settings = self.load_config(path, **kwargs)
        except (json.JSONDecodeError, yaml.YAMLError):
            return False
        begin = settings
        for p in mcp_path:
            begin = begin.get(p, {})
        begin = mcp_settings

        current = settings
        path_length = len(mcp_path)

        for i, p in enumerate(mcp_path):
            if i == path_length - 1:
                current[p] = mcp_settings
                break

            if p not in current or not isinstance(current[p], dict):
                current[p] = {}

            current = current[p]

        try:
            with open(path, "w") as f:
                self.saver(settings, f)
            Settings.logger.print(
                Markdown(f"Successfully updated `{path}` with Pieces configuration")
            )
        except Exception as e:
            Settings.logger.print(f"Error writing {self.readable} {dirname}")
            raise e
        Settings.mcp_config.add_project(self.id, mcp_type, path)
        return True

    def load_config(self, path: str = "", **kwargs) -> Dict:
        if not path:
            path = self.get_settings_path(**kwargs)
        try:
            with open(path, "r") as f:
                settings = self.loader(f)
        except FileNotFoundError as e:
            parent_dir = os.path.dirname(path)

            if os.path.exists(parent_dir):
                return {}
            raise e  # @tsavo-at-pieces Do we need to create the file? or just raise the error?
        except (json.JSONDecodeError, yaml.YAMLError):
            if os.path.getsize(path) == 0:
                return {}
            Settings.logger.print(
                f"Failed in prasing {self.readable}, {path} - it may be malformed"
            )
            raise

        return settings

    def exists(self) -> bool:
        return self.check_command_existence() or self.check_paths_existence()

    def check_command_existence(self) -> bool:
        return (
            shutil.which(self.check_existence_command) is not None
            if self.check_existence_command
            else False
        )

    def check_paths_existence(self) -> bool:
        for path in self.check_existence_paths:
            if os.path.exists(path):
                return True
        return False

    def need_repair(
        self,
    ) -> IntegrationDict:
        """
        Checking for every project in the local cache ONLY
        Checking all attributes if they are good to go
            1. Searching for the correct URL if found we check for repairs in the other values as well
            If any of these not found we remove it from the local cache (the user removed it already and don't want it)
        Returns: list of the paths that needs to be repaired
        """
        paths = Settings.mcp_config.get_projects(self.id)
        paths_to_remove = []
        paths_to_repair: IntegrationDict = {}
        for path, mcp_type in paths.items():
            check, config = self.search(path, mcp_type)
            if check:
                if not self.check_properties(mcp_type, config):
                    paths_to_repair[path] = mcp_type
            else:
                ## Try searching any property with Pieces maybe
                appended = False
                for key in config:
                    if key.lower() in "pieces":
                        ## might be an issue here because it is already in the local cache
                        paths_to_repair[path] = mcp_type
                        appended = True
                        break
                if not appended:
                    # SADLY let's removed from the local cache
                    paths_to_remove.append(path)

        [Settings.mcp_config.remove_project(self.id, path) for path in paths_to_remove]

        return paths_to_repair

    def check_properties(self, mcp_type: mcp_types, config: Dict) -> bool:
        mcp_settings = self.mcp_properties.mcp_modified_settings(mcp_type)
        for k, value in config.items():
            if k == self.mcp_properties.url_property_name and mcp_type == "sse":
                if value != get_mcp_latest_url():
                    return False
            elif k in mcp_settings:
                if mcp_settings[k] != value:
                    return False
            else:
                return False
        return True

    def is_set_up(self) -> bool:
        """
        Checks for the local cache and the global paths as well
        This should check for 2 things
        1. Valid url in any property has Pieces
        2. Add it to the cache if yes
        """

        # Search in the global path might be set up be the user manually
        gb = self.get_settings_path()
        for mcp_type in self.mcp_types:
            if self.search(gb, mcp_type)[0]:
                Settings.mcp_config.add_project(self.id, mcp_type, gb)
                return True

        paths = Settings.mcp_config.get_projects(self.id)
        for path, mcp_type in paths.items():
            if self.search(path, mcp_type=mcp_type)[0]:
                return True

        return False

    def search(self, path: str, mcp_type: mcp_types) -> Tuple[bool, Dict]:
        """
        Search for any potential pieces mcp (matching the properties/url) and the name pieces

        Args:
            path: path to seach for
            mcp_type: the mcp type of that path to match it

        Returns:
            Tuple of a boolean (there is a potential already setted up mcp in that path), Dict the config in that path
        """
        try:
            config = self.load_config(path or "")
        except FileNotFoundError:
            return False, {}
        except (json.JSONDecodeError, yaml.YAMLError):
            return False, {}

        # Ignore the Pieces because it might be named anything else
        for p in self.mcp_properties.mcp_path(mcp_type)[:-1]:
            config = config.get(p, {})
        for k in config.keys():
            if not isinstance(config[k], dict):
                continue
            if mcp_type == "sse":
                if (
                    config[k].get(self.mcp_properties.url_property_name, "")
                    in get_mcp_urls()
                ):
                    return True, config[k]
            else:
                if (
                    config[k].get(self.mcp_properties.command_property_name, "")
                    == self.mcp_properties.pieces_cli_bin_path
                ):
                    return True, config[k]

        return False, config

    def __str__(self) -> str:
        return self.readable
