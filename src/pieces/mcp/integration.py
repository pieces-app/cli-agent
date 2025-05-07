import json
import os
from typing import Callable, Dict, List, Tuple, Optional
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
import time
import urllib3
import yaml

from pieces.settings import Settings

from .utils import get_mcp_latest_url, get_mcp_urls
from ..utils import PiecesSelectMenu


class ConditionalSpinnerColumn(SpinnerColumn):
    def render(self, task):
        if task.completed:
            return ""
        return super().render(task)


class Integration:
    def __init__(
        self,
        options: List[Tuple],
        text_success: str,
        readable: str,
        docs: str,
        get_settings_path: Callable,
        path_to_mcp_settings: List[str],
        mcp_settings: Dict,
        error_text: Optional[str] = None,
        loader=json.load,
        saver=lambda x, y: json.dump(x, y, indent=4),
        url_property_name="url",
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
        self.path_to_mcp_settings = path_to_mcp_settings
        self.mcp_settings = mcp_settings
        self.loader = loader
        self.saver = saver
        self.url_property_name = url_property_name
        self.console = Settings.logger.console
        self.id: str = id or self.readable.lower().replace(" ", "_")

    def handle_options(self, **kwargs):
        if self.options and not kwargs:
            return PiecesSelectMenu(self.options, self.on_select).run()
        else:
            self.on_select(**kwargs)
            return True

    def run(self, **kwargs):
        self.console.print(f"Attempting to update Global {self.readable} MCP Tooling")
        if not self.check_ltm():
            return
        try:
            if not self.handle_options(**kwargs):
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
            self.console.print(Markdown(self.error_text))

    @classmethod
    def load_mcp_config(cls):
        try:
            with open(Settings.mcp_config, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @classmethod
    def add_project(cls, integration: str, path: str):
        config = cls.load_mcp_config()
        c = config.get(integration, [])
        c.append(path)
        # avoid duplicates
        config[integration] = list(set(c))
        with open(Settings.mcp_config, "w") as f:
            json.dump(config, f)

    def remove_project(self, path: str):
        config = self.load_mcp_config()
        c = config.get(self.id, [])
        try:
            c.remove(path)
        except ValueError:
            pass
        config[self.id] = c
        with open(Settings.mcp_config, "w") as f:
            json.dump(config, f)

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

    def _open_ltm(self):
        try:
            Settings.pieces_client.copilot.context.ltm.enable(
                False
            )  # Don't show any permission notification/pop up
        except Exception as e:
            Settings.show_error(f"Error in enabling the LTM: {e}")

    def repair(self):
        paths_to_repair = self.need_repair()
        if paths_to_repair:
            [self.on_select(p) for p in paths_to_repair]
        else:
            self.console.print(f"No issues detected in {self.readable}")

    def on_select(self, path=None, **kwargs):
        self.mcp_settings[self.url_property_name] = get_mcp_latest_url()
        if not path:
            path = self.get_settings_path(**kwargs)
        dirname = os.path.dirname(path)
        settings = self.load_config(path, **kwargs)
        begin = settings
        for p in self.path_to_mcp_settings:
            begin = begin.get(p, {})
        begin = self.mcp_settings

        current = settings
        path_length = len(self.path_to_mcp_settings)

        for i, p in enumerate(self.path_to_mcp_settings):
            if i == path_length - 1:
                current[p] = self.mcp_settings
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
        self.add_project(self.id, path)

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

    def need_repair(self) -> list:
        """
        Checking for every project in the local cache ONLY
        Checking all attributes if they are good to go
            1. Searching for the correct URL if found we check for repairs in the other values as well
            If any of these not found we remove it from the local cache (the user removed it already and don't want it)
        Returns: list of the paths that needs to be repaired
        """
        paths = self.load_mcp_config().get(self.id, [])
        paths_to_repair = []
        for path in paths:
            check, config = self.search(path)
            # Check is True
            if check:
                if not self.check_properties(config):
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
                    self.remove_project(path)

        return paths_to_repair

    def check_properties(self, config) -> bool:
        for k, value in config.items():
            if k == self.url_property_name:
                if value != get_mcp_latest_url():
                    return False
            elif k in self.mcp_settings:
                if self.mcp_settings[k] != value:
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
        paths = self.load_mcp_config().get(self.id, [])
        gb = self.get_settings_path()

        if gb not in paths and self.search(gb)[0]:
            self.add_project(self.id, gb)
            return True

        return any([self.search(path)[0] for path in paths])

    def search(self, path: str) -> Tuple[bool, Dict]:
        try:
            config = self.load_config(path or "")
        except FileNotFoundError:
            return False, {}
        except ValueError as e:
            print(e)
            return False, {}

        # Ignore the Pieces because it might be named anything else
        for p in self.path_to_mcp_settings[:-1]:
            config = config.get(p, {})
        for k in config.keys():
            if config[k].get(self.url_property_name, "") in get_mcp_urls():
                return True, config[k]

        return False, config

    def __str__(self) -> str:
        return self.readable
