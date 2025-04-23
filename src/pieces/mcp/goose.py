import yaml
import os
from ..settings import Settings


config_path = os.path.expanduser("~/.config/goose/config.yaml")


def handle_goose():
    new_extension = {
        "pieces": {
            "bundled": None,
            "description": "Pieces MPC",
            "enabled": True,
            "env_keys": [],
            "envs": {},
            "name": "Pieces",
            "timeout": 300,
            "type": "sse",
            # TODO: @bishoy-at-pieces
            "uri": "http://localhost:39300/model_context_protocol/2024-11-05/sse",
        }
    }

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as file:
                config = yaml.safe_load(file) or {}
        except Exception as e:
            print(f"Error reading config file: {e}")
            config = {}
    else:
        Settings.show_error(f"Goose configurations is not found at {config_path}")
        raise ValueError

    if "extensions" not in config:
        config["extensions"] = {}

    if config["extensions"] is None:
        config["extensions"] = {}
    config["extensions"].update(new_extension)

    with open(config_path, "w") as file:
        yaml.dump(config, file, default_flow_style=False)

    print(f"Configuration updated and saved to {config_path}")
