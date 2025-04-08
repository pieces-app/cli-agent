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
            print(f"Editor set to: {kwargs['editor']}")
        else:
            print("Current configuration:")
            print(f"Editor: {config.get('editor', 'Not set')}")
            print(f"Remote execution: {'Enabled' if config.get('remote_enabled', False) else 'Disabled'}")

    @classmethod
    def get_remote_config(cls):
        """Get the current remote configuration"""
        config = cls.load_config()
        return {
            'enabled': config.get('remote_enabled', False),
            'host': config.get('remote_host', ''),
            'username': config.get('remote_username', ''),
            'method': config.get('remote_method', ''),
            'password': config.get('remote_password', ''),
            'key_file': config.get('remote_key_file', '')
        }

    @classmethod
    def set_remote_config(cls, config):
        """Set the remote configuration"""
        current_config = cls.load_config()
        current_config.update({
            'remote_enabled': config.get('enabled', False),
            'remote_host': config.get('host', ''),
            'remote_username': config.get('username', ''),
            'remote_method': config.get('method', ''),
            'remote_password': config.get('password', ''),
            'remote_key_file': config.get('key_file', '')
        })
        cls.save_config(current_config)

    @classmethod
    def toggle_remote(cls, enable: bool):
        """Enable/disable remote execution"""
        config = cls.load_config()
        config['remote_enabled'] = enable
        cls.save_config(config)
        print(f"Remote execution {'enabled' if enable else 'disabled'}")
