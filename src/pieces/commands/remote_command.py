from pieces.settings import Settings
import paramiko
from typing import Optional, Dict, Any
import os
import json
from pieces.commands.config_command import ConfigCommands

class RemoteCommand:
    @classmethod
    def execute_command(cls, **kwargs):
        """Main entry point for 'pieces remote' command"""
        subcommand = kwargs.get('subcommand', 'status')
        
        if subcommand == 'setup':
            cls.setup_remote()
        elif subcommand == 'enable':
            ConfigCommands.toggle_remote(True)
        elif subcommand == 'disable':
            ConfigCommands.toggle_remote(False)
        elif subcommand == 'status':
            cls._show_status()
        else:
            print("Available subcommands:")
            print("  setup   - Configure remote connection settings")
            print("  enable  - Enable remote execution")
            print("  disable - Disable remote execution")
            print("  status  - Show current remote configuration")

    @classmethod
    def _show_status(cls):
        """Show current remote configuration status"""
        config = ConfigCommands.get_remote_config()
        if not config['enabled']:
            print("Remote execution is disabled")
            print("Run 'pieces remote setup' to configure remote settings")
            return
            
        print("Remote execution configuration:")
        print(f"Status: {'Enabled' if config['enabled'] else 'Disabled'}")
        print(f"Host: {config['host']}")
        print(f"Username: {config['username']}")
        print(f"Method: {config['method']}")

    @classmethod
    def setup_remote(cls):
        """Interactive setup for remote connection settings"""
        print("\nRemote Connection Setup")
        print("----------------------")
        
        # Get connection method
        method = input("Connection method (password/key): ").lower()
        while method not in ['password', 'key']:
            print("Invalid method. Please choose 'password' or 'key'")
            method = input("Connection method (password/key): ").lower()
        
        # Get connection details
        host = input("Remote host: ").strip()
        username = input("Username: ").strip()
        
        if method == 'password':
            password = input("Password: ").strip()
            key_file = None
        else:
            password = None
            key_file = input("Path to SSH key file: ").strip()
            key_file = os.path.expanduser(key_file)
        
        # Validate settings
        if cls.validate_remote_settings(host, username, password, key_file):
            # Test connection
            try:
                client = cls.setup_remote_connection(host, username, password, key_file)
                client.close()
                print("Connection test successful!")
                
                # Save settings
                config = {
                    'host': host,
                    'username': username,
                    'method': method,
                    'password': password if method == 'password' else None,
                    'key_file': key_file if method == 'key' else None
                }
                ConfigCommands.set_remote_config(config)
                print("Remote settings saved successfully!")
                
            except Exception as e:
                print(f"Connection test failed: {e}")
                return False
        else:
            print("Invalid remote settings. Please try again.")
            return False
            
        return True

    @classmethod
    def validate_remote_settings(cls, host: str, username: str, 
                               password: Optional[str] = None, 
                               key_file: Optional[str] = None) -> bool:
        """Validate remote settings"""
        if not host or not username:
            return False
            
        if not password and not key_file:
            return False
            
        if key_file and not os.path.exists(key_file):
            return False
            
        return True

    @classmethod
    def setup_remote_connection(cls, host: str, username: str, 
                               password: Optional[str] = None, 
                               key_file: Optional[str] = None) -> 'paramiko.SSHClient':
        """Set up SSH connection"""
        if not cls.validate_remote_settings(host, username, password, key_file):
            raise ValueError("Invalid remote settings provided")
            
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        try:
            if key_file:
                client.connect(host, username=username, key_filename=key_file)
            else:
                client.connect(host, username=username, password=password)
            return client
        except Exception as e:
            raise Exception(f"Failed to connect to remote host: {str(e)}")

    @classmethod
    def execute_remote_command(cls, client: 'paramiko.SSHClient', 
                             command: str) -> Dict[str, str]:
        """Execute remote command"""
        try:
            stdin, stdout, stderr = client.exec_command(command)
            return {
                'stdout': stdout.read().decode(),
                'stderr': stderr.read().decode()
            }
        except Exception as e:
            raise Exception(f"Failed to execute remote command: {str(e)}")

    @classmethod
    def close_connection(cls, client: 'paramiko.SSHClient'):
        """Close SSH connection"""
        client.close()