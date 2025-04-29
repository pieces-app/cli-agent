import json
import os
from typing import Callable, Dict, List, Literal, Tuple, Optional
from rich.console import Console
from rich.markdown import Markdown
import yaml

from pieces.settings import Settings

from .utils import get_mcp_latest_url, get_mcp_urls
from ..utils import PiecesSelectMenu


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
        id=Optional[str],
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
        self.console = Console()
        self.id = id or self.readable.lower().replace(" ", "_")

    def handle_options(self, **kwargs):
        if self.options and not kwargs:
            PiecesSelectMenu(self.options, self.on_select).run()
        else:
            self.on_select(**kwargs)

    def run(self, **kwargs):
        if not self.check_ltm():
            return
        try:
            self.handle_options(**kwargs)
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
        except FileNotFoundError:
            return {}

    @classmethod
    def add_local_project(
        cls, integration: Literal["vscode", "goose", "cursor"], path: str
    ):
        config = cls.load_mcp_config()
        c = config.get(integration, [])
        c.append(path)
        # avoid duplicates
        config[integration] = list(set(c))
        with open(Settings.mcp_config, "w") as f:
            json.dump(config, f)

    def check_ltm(self) -> bool:
        # Update the local cache
        Settings.pieces_client.copilot.context.ltm.ltm_status = Settings.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status()
        if not Settings.pieces_client.copilot.context.ltm.is_enabled:
            if (
                self.console.input(
                    "Pieces LTM must be running, do you want to enable it? (y/n): ",
                    markup=True,
                )
                .lower()
                .strip()
                == "y"
            ):
                try:
                    Settings.pieces_client.copilot.context.ltm.enable(True)
                except PermissionError as e:
                    css_selector = "#installing-piecesos--configuring-permissions"
                    self.console.print("Could not enable the LTM")
                    self.console.print(self.docs_no_css_selector + css_selector)
                    self.console.print(Markdown(f"**{e}**"))
                    return False
            else:
                return False
        return True

    def repair(self):
        if self.need_repair():
            self.on_select()
        else:
            self.console.print(f"No issues detected in {self.readable}")

    def on_select(self, **kwargs):
        self.mcp_settings[self.url_property_name] = get_mcp_latest_url()
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
        if kwargs.get("option", None) == "local":
            self.add_local_project(self.id, path)

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

    def need_repair(self) -> bool:
        return not self._is_set_up()

    def is_set_up(self) -> bool:
        return self._is_set_up(False)

    def _is_set_up(self, url=True) -> bool:
        try:
            config = self.load_config()
        except FileNotFoundError:
            return False
        except ValueError as e:
            print(e)
            return False
        # Ignore the server name (Pieces)
        for p in self.path_to_mcp_settings[:-1]:
            config = config.get(p, {})

        for server in config.values():
            if isinstance(server, dict) and server.get(self.url_property_name):
                if url and server.get(self.url_property_name) in get_mcp_urls():
                    return True
                return True
        return False

    def __str__(self) -> str:
        return self.readable
