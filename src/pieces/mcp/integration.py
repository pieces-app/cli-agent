import json
import os
from typing import Callable, Dict, List, Literal, Tuple, Optional, TypedDict, get_args

from rich.markdown import Markdown
import yaml
import sys

from pieces.copilot.ltm import check_ltm
from pieces.settings import Settings

from .utils import get_mcp_latest_url, get_mcp_urls
from ..utils import PiecesSelectMenu

MCP_types = Literal["sse", "stdio"]

IntegrationDict = Dict[str, MCP_types]

mcp_integration_types = Literal[
    "vscode", "goose", "cursor", "claude", "windsurf", "zed", "shortwave", "claude_code"
]
mcp_integrations: List[mcp_integration_types] = list(get_args(mcp_integration_types))


class ConfigDict(TypedDict, total=False):
    schema: str
    vscode: IntegrationDict
    cursor: IntegrationDict
    goose: IntegrationDict
    claude: IntegrationDict
    windsurf: IntegrationDict
    zed: IntegrationDict
    shortwave: IntegrationDict
    claude_code: IntegrationDict


class MCPLocalConfig:
    DEFAULT_SCHEMA = "0.0.0"
    DEFAULT_INTEGRATIONS = mcp_integrations

    def __init__(self) -> None:
        self.config: ConfigDict = self.load_config()
        self.migrate_json()

    def load_config(self) -> ConfigDict:
        try:
            with open(Settings.mcp_config, "r") as f:
                raw = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            raw = {}

        # Normalize the config structure
        config: ConfigDict = {"schema": self.DEFAULT_SCHEMA}
        for integration in self.DEFAULT_INTEGRATIONS:
            config[integration] = raw.get(integration, {})

        # Preserve schema if it exists
        if "schema" in raw:
            config["schema"] = raw["schema"]

        return config

    def migrate_json(self):
        if self.config.get("schema", None) == "0.0.1":
            return

        for k, v in self.config.items():
            if isinstance(v, list):
                self.config[k] = dict.fromkeys(v, "stdio")
        self.config["schema"] = "0.0.1"
        self.save_config()

    def save_config(self):
        with open(Settings.mcp_config, "w") as f:
            json.dump(self.config, f)

    def add_project(self, integration: str, mcp_type: MCP_types, path: str):
        paths = self.get_projects(integration)
        paths[path] = mcp_type
        self.config[integration] = paths
        self.save_config()

    def remove_project(self, integration: str, path: str):
        c = self.get_projects(integration)
        try:
            c.pop(path)
        except KeyError:
            pass
        self.config[integration] = c
        self.save_config()

    def get_projects(self, integration: str) -> IntegrationDict:
        return self.config.get(integration, {})


class MCPProperties:
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
        # Better than shutil.which if pieces is not added to the path
        self.pieces_cli_bin_path = os.path.abspath(sys.argv[0])

    def mcp_settings(self, mcp_type: MCP_types):
        if mcp_type == "sse":
            return self.sse_property
        else:
            return self.stdio_property

    def mcp_path(self, mcp_type: MCP_types):
        if mcp_type == "sse":
            return self.sse_path
        else:
            return self.stdio_path

    def mcp_modified_settings(self, mcp_type: MCP_types):
        mcp_settings = self.mcp_settings(mcp_type)
        if mcp_type == "sse":
            mcp_settings[self.url_property_name] = get_mcp_latest_url()
        else:
            mcp_settings[self.command_property_name] = self.pieces_cli_bin_path
            mcp_settings[self.args_property_name] = ["--ignore-onboarding", "mcp", "start"]
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
        error_text: Optional[str] = None,
        loader=json.load,
        saver=lambda x, y: json.dump(x, y, indent=4),
        id: Optional[str] = None,
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
        self.docs = docs
        self.get_settings_path = get_settings_path
        self.loader = loader
        self.saver = saver
        self.console = Settings.logger.console
        self.id: str = id or self.readable.lower().replace(" ", "_")
        self._local_config = None
        self.mcp_properties = mcp_properties
        self.mcp_types: List[MCP_types] = ["sse", "stdio"]

    @property
    def local_config(self):
        if not self._local_config:
            self._local_config = MCPLocalConfig()
        return self._local_config

    def handle_options(self, stdio: bool, **kwargs):
        mcp_type = "stdio" if stdio else "sse"
        for option in range(len(self.options)):
            self.options[option][1]["mcp_type"] = mcp_type

        if self.options and not kwargs:
            return PiecesSelectMenu(self.options, self.on_select).run()
        else:
            return self.on_select(mcp_type, **kwargs)

    def run(self, stdio: bool, **kwargs):
        if stdio and not self.mcp_properties.pieces_cli_bin_path:
            raise ValueError(
                "Pieces Cli is not added to the path you can't setup the stdio servers please add it to the path"
            )
        self.console.print(f"Attempting to update Global {self.readable} MCP Tooling")
        if not self.check_ltm():
            return
        try:
            if not self.handle_options(stdio, **kwargs):
                return
            self.console.print(
                Markdown(f"✅ Pieces MCP is now enabled for {self.readable}!")
            )
            self.console.print(
                Markdown(
                    f"For more information please refer to the docs: `{self.docs}`"
                )
            )
            self.console.print(Markdown(self.text_end))
        except KeyboardInterrupt:
            pass
        except Exception as e:  # noqa: E722
            print(e)
            Settings.logger.critical(e)
            self.console.print(Markdown(self.error_text))

    def check_ltm(self) -> bool:
        css_selector = "#installing-piecesos--configuring-permissions"
        return check_ltm(self.docs_no_css_selector + css_selector)

    def repair(self):
        paths_to_repair = self.need_repair()
        if paths_to_repair:
            [self.on_select(mcp_type, p) for p, mcp_type in paths_to_repair.items()]
        else:
            self.console.print(f"No issues detected in {self.readable}")

    def on_select(self, mcp_type: MCP_types, path=None, **kwargs) -> bool:
        mcp_settings = self.mcp_properties.mcp_modified_settings(mcp_type)
        mcp_path = self.mcp_properties.mcp_path(mcp_type)
        if not path:
            path = self.get_settings_path(**kwargs)
        old_mcp_type = self.local_config.get_projects(self.id).get(path, mcp_type)
        if (
            old_mcp_type != mcp_type
            and self.search(path, old_mcp_type)[0]  # the old set up and NOT removed
            and not Settings.logger.confirm(
                f"{mcp_type} is already used as your {self.readable} MCP\n"
                f"Do you want to replace the {old_mcp_type} mcp with the {mcp_type} mcp?"
            )
        ):
            return False
        dirname = os.path.dirname(path)
        settings = self.load_config(path, **kwargs)
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
            print(f"Successfully updated {path} with Pieces configuration")
        except Exception as e:
            print(f"Error writing {self.readable} {dirname}")
            raise e
        self.local_config.add_project(self.id, mcp_type, path)
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
            print(f"Failed in prasing {self.readable}, {path} - it may be malformed")
            raise ValueError

        return settings

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
        paths = self.local_config.get_projects(self.id)
        paths_to_repair: IntegrationDict = {}
        for path, mcp_type in paths.items():
            check, config = self.search(path, mcp_type)
            # Check is True
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
                    self.local_config.remove_project(self.id, path)

        return paths_to_repair

    def check_properties(self, mcp_type: MCP_types, config: Dict) -> bool:
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
                self.local_config.add_project(self.id, mcp_type, gb)
                return True

        paths = self.local_config.get_projects(self.id)
        for path, mcp_type in paths.items():
            if self.search(path, mcp_type=mcp_type)[0]:
                return True

        return False

    def search(self, path: str, mcp_type: MCP_types) -> Tuple[bool, Dict]:
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
        except ValueError as e:
            print(e)
            return False, {}

        # Ignore the Pieces because it might be named anything else
        for p in self.mcp_properties.mcp_path(mcp_type)[:-1]:
            config = config.get(p, {})
        for k in config.keys():
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
