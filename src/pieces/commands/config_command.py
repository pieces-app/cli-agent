import os
from pieces.settings import Settings
import json



class ConfigCommands:
    @classmethod
    def load_config(cls):
        if os.path.exists(Settings.config_file):
            try:
                with open(Settings.config_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
                    else:
                        # print("Config file is empty. Creating a new configuration.")
                        return {}
            except json.JSONDecodeError:
                print("Invalid JSON in config file. Creating a new configuration.")
                return {}
        else:
            # print("Config file does not exist. Creating a new configuration.")
            return {}

    @classmethod
    def save_config(cls, config):
        with open(Settings.config_file, 'w') as f:
            json.dump(config, f)

    @classmethod
    def config(cls, **kwargs):
        config = cls.load_config()
        if 'editor' in kwargs:
            config['editor'] = kwargs['editor']
            cls.save_config(config)
            print(f"Editor set to: {kwargs['editor']}")
        else:
            print("Current configuration:")
            print(f"Editor: {config.get('editor', 'Not set')}")
