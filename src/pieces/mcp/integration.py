import json
import os
from typing import Callable, Dict, List, Literal, Tuple, Optional
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import urllib3
import yaml

from pieces.settings import Settings

from .utils import get_mcp_latest_url, get_mcp_urls
from ..utils import PiecesSelectMenu

MCP_types = Literal["sse", "stdio"]


class ConditionalSpinnerColumn(SpinnerColumn):
    def render(self, task):
        if task.completed:
            return ""
        return super().render(task)


class MCPLocalConfig:
    def __init__(self) -> None:
        self.config: Dict = self.load_config()
        self.migrate_json()

    def load_config(self):
        try:
            with open(Settings.mcp_config, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def migrate_json(self):
        if self.config.get("schema", None):
            return

        for k, v in self.config.items():
            if isinstance(v, Dict):
                return
            if isinstance(v, list):
                self.config[k] = {}
                self.config[k]["stdio"] = []
                self.config[k]["sse"] = v
        self.config["schema"] = "0.0.1"
        self.save_config()

    def save_config(self):
        with open(Settings.mcp_config, "w") as f:
            json.dump(self.config, f)

    def add_project(self, integration: str, mcp_type: MCP_types, path: str):
        c = self.config.get(integration, {}).get(mcp_type, [])
        c.append(path)
        # avoid duplicates
        self.config[integration] = self.config.get(integration, {})  # Type safety
        self.config[integration][mcp_type] = list(set(c))
        self.save_config()

    def remove_project(self, integration: str, mcp_type: MCP_types, path: str):
        c = self.config.get(integration, {})
        try:
            c.get(mcp_type, []).remove(path)
        except ValueError:
            pass
        self.config[integration] = c
        self.save_config()

    def get_projects(self, integration: str, mcp_type: MCP_types):
        return self.config.get(integration, {}).get(mcp_type, [])


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
            mcp_settings[self.command_property_name] = "pieces"
            mcp_settings[self.args_property_name] = ["mcp", "start"]
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
            self.on_select(mcp_type, **kwargs)
            return True

    def run(self, stdio: bool, **kwargs):
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
        # Update the local cache
        Settings.pieces_client.copilot.context.ltm.ltm_status = Settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status()
        if Settings.pieces_client.copilot.context.ltm.is_enabled:
            return True

        if not Settings.logger.confirm(
            "Pieces LTM must be running, do you want to enable it?",
        ):
            return False
        missing_permissions = Settings.pieces_client.copilot.context.ltm.check_perms()
        if not missing_permissions:
            self._open_ltm()
            return True

        with Progress(
            ConditionalSpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=False,
        ) as progress:
            css_selector = "#installing-piecesos--configuring-permissions"
            self.console.print(self.docs_no_css_selector + css_selector)
            vision_task = progress.add_task(
                "[cyan]Vision permission: checking...",
            )
            accessibility_task = progress.add_task(
                "[cyan]Accessibility permission: checking...",
            )
            main_task = progress.add_task(
                "[cyan]Checking PiecesOS permissions...", total=None
            )
            permissions_len = 100

            while True:
                try:
                    missing_permissions = (
                        Settings.pieces_client.copilot.context.ltm.check_perms()
                    )
                    if len(missing_permissions) < permissions_len:
                        # at least there is a progress here let's show the message again
                        show_message = True
                    else:
                        show_message = False

                    permissions_len = len(missing_permissions)
                    if "vision" not in missing_permissions:
                        progress.update(
                            vision_task,
                            description="[green]Vision permission: enabled",
                            completed=True,
                        )
                    else:
                        progress.update(
                            vision_task,
                            description="[yellow]Vision permission: enabling...",
                        )
                    if "accessibility" not in missing_permissions:
                        progress.update(
                            accessibility_task,
                            description="[green]Accessibility permission: enabled",
                            completed=True,
                        )
                    else:
                        progress.update(
                            accessibility_task,
                            description="[yellow]Accessibility permission: enabling...",
                        )

                    if not missing_permissions:
                        progress.update(
                            main_task,
                            description="[green]All permissions are activiated",
                            completed=True,
                        )
                        break

                    progress.update(
                        main_task,
                        description=f"[yellow]Found {permissions_len} missing permissions",
                    )

                    if show_message:
                        Settings.pieces_client.copilot.context.ltm.enable(True)
                    else:
                        time.sleep(3)  # 3 sec delay
                except PermissionError:
                    pass
                except (
                    urllib3.exceptions.ProtocolError,
                    urllib3.exceptions.NewConnectionError,
                    urllib3.exceptions.ConnectionError,
                    urllib3.exceptions.MaxRetryError,
                ):  # Hope we did not forgot any exception
                    progress.update(
                        main_task,
                        description="[yellow]PiecesOS is restarting...",
                    )

                    progress.update(vision_task, visible=False)
                    progress.update(accessibility_task, visible=False)

                    if Settings.pieces_client.is_pieces_running(maxium_retries=10):
                        missing_permissions = (
                            Settings.pieces_client.copilot.context.ltm.check_perms()
                        )
                        if not missing_permissions:
                            progress.update(
                                main_task,
                                description="[green]All permissions are enabled!",
                                completed=True,
                            )
                            time.sleep(0.5)
                            break
                        else:
                            progress.update(vision_task, visible=True)
                            progress.update(accessibility_task, visible=True)
                    else:
                        progress.update(
                            main_task,
                            description="[red]Failed to open PiecesOS",
                            completed=True,
                        )
                        time.sleep(1)
                        return False
                except KeyboardInterrupt:
                    progress.update(vision_task, visible=False)
                    progress.update(accessibility_task, visible=False)

                    progress.update(
                        main_task,
                        description="[red]Operation cancelled by user",
                        completed=True,
                    )
                    return False
                except Exception as e:
                    progress.update(vision_task, visible=False)
                    progress.update(accessibility_task, visible=False)

                    progress.update(
                        main_task,
                        description=f"[red]Unexpected error: {str(e)}",
                        completed=True,
                    )
                    return False
            self._open_ltm()

            return True

    @staticmethod
    def _open_ltm():
        try:
            Settings.pieces_client.copilot.context.ltm.enable(
                False
            )  # Don't show any permission notification/pop up
        except Exception as e:
            Settings.show_error(f"Error in enabling the LTM: {e}")

    def repair(self):
        for mcp_mcp_type in self.mcp_types:
            paths_to_repair = self.need_repair(mcp_mcp_type)
            if paths_to_repair:
                [self.on_select(p) for p in paths_to_repair]
            else:
                self.console.print(f"No issues detected in {self.readable}")

    def on_select(self, mcp_type: MCP_types, path=None, **kwargs):
        mcp_settings = self.mcp_properties.mcp_modified_settings(mcp_type)
        mcp_path = self.mcp_properties.mcp_path(mcp_type)
        if not path:
            path = self.get_settings_path(**kwargs)
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

    def load_config(self, path: str = "", **kwargs) -> Dict:
        if not path:
            path = self.get_settings_path(**kwargs)
        try:
            with open(path, "r") as f:
                settings = self.loader(f)
        except FileNotFoundError as e:
            raise e
        except (json.JSONDecodeError, yaml.YAMLError):
            print(f"Failed in prasing {self.readable}, {path} - it may be malformed")
            raise ValueError

        return settings

    def need_repair(self, mcp_type: MCP_types) -> list:
        """
        Checking for every project in the local cache ONLY
        Checking all attributes if they are good to go
            1. Searching for the correct URL if found we check for repairs in the other values as well
            If any of these not found we remove it from the local cache (the user removed it already and don't want it)
        Returns: list of the paths that needs to be repaired
        """
        paths = self.local_config.get_projects(self.id, mcp_type)
        paths_to_repair = []
        for path in paths:
            check, config = self.search(path, mcp_type)
            # Check is True
            if check:
                if not self.check_properties(mcp_type, config):
                    paths_to_repair.append(path)
            else:
                ## Try searching any property with Pieces maybe
                appended = False
                for key in config:
                    if key.lower() in "pieces":
                        ## might be an issue here because it is already in the local cache
                        paths_to_repair.append(path)
                        appended = True
                        break
                if not appended:
                    # SADLY let's removed from the local cache
                    self.local_config.remove_project(self.id, mcp_type, path)

        return paths_to_repair

    def check_properties(self, mcp_type: MCP_types, config) -> bool:
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
        for mcp_type in self.mcp_types:
            paths = self.mcp_properties.mcp_settings(mcp_type)
            gb = self.get_settings_path()

            if self.search(gb, mcp_type)[0]:
                self.local_config.add_project(self.id, mcp_type, gb)
                return True

            for path in paths:
                if self.search(path, mcp_type=mcp_type)[0]:
                    return True

        return False

    def search(self, path: str, mcp_type: MCP_types) -> Tuple[bool, Dict]:
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
                    == "pieces"
                ):
                    return True, config[k]

        return False, config

    def __str__(self) -> str:
        return self.readable
