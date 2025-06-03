import os
from pieces.settings import Settings
import json


class ConfigCommands:
    config_data = None

    @classmethod
    def load_config(cls):
        if cls.config_data:
            return cls.config_data
        if os.path.exists(Settings.config_file):
            try:
                with open(Settings.config_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        cls.config_data = json.loads(content)
                    else:
                        cls.config_data = {}
            except json.JSONDecodeError:
                cls.config_data = {}
        else:
            cls.config_data = {}
        return cls.config_data

    @classmethod
    def save_config(cls, config):
        with open(Settings.config_file, 'w') as f:
            json.dump(config, f)

    @classmethod
    def config(cls, **kwargs):
        config = cls.load_config()
        editor = kwargs.get("editor")
        if editor:
            config['editor'] = editor
            cls.save_config(config)
            Settings.logger.print(f"Editor set to: {kwargs['editor']}")
        else:
            Settings.logger.print("Current configuration:")
            Settings.logger.print(f"Editor: {config.get('editor', 'Not set')}")
