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
        command = kwargs.get('command', None)
        
        if subcommand == 'setup':
            cls.setup_remote()
        elif subcommand == 'enable':
            ConfigCommands.toggle_remote(True)
        elif subcommand == 'disable':
            ConfigCommands.toggle_remote(False)
        elif subcommand == 'status':
            cls._show_status()
        elif subcommand == 'test':
            cls.test_connection(command)
        else:
            print("Available subcommands:")
            print("  setup   - Configure remote connection settings")
            print("  enable  - Enable remote execution")
            print("  disable - Disable remote execution")
            print("  status  - Show current remote configuration")
            print("  test    - Test the remote connection with an optional command")

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
                              key_file: Optional[str] = None) -> paramiko.SSHClient:
        """Set up an SSH connection to the remote host"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        if password:
            client.connect(host, username=username, password=password)
        else:
            key = paramiko.RSAKey.from_private_key_file(key_file)
            client.connect(host, username=username, pkey=key)
            
        return client

    @classmethod
    def close_connection(cls, client: paramiko.SSHClient):
        """Close the SSH connection"""
        if client:
            client.close()

    @classmethod
    def execute_remote_command(cls, client: paramiko.SSHClient, command: str) -> str:
        """Execute a command on the remote system and return the output"""
        stdin, stdout, stderr = client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        
        if error:
            raise Exception(f"Remote command failed: {error}")
            
        return output

    @classmethod
    def test_connection(cls, command: Optional[str] = None):
        """Test the remote connection by executing a simple command"""
        config = ConfigCommands.get_remote_config()
        if not config['enabled']:
            print("Remote execution is disabled. Use 'pieces remote enable' to enable it.")
            return False
            
        try:
            client = cls.setup_remote_connection(
                config['host'],
                config['username'],
                config['password'] if config['method'] == 'password' else None,
                config['key_file'] if config['method'] == 'key' else None
            )
            
            # Execute a test command
            print("\nTesting remote connection...")
            
            if command:
                print(f"\nExecuting user command: {command}")
                try:
                    output = cls.execute_remote_command(client, command)
                    print(f"\nCommand output:\n{output}")
                except Exception as e:
                    print(f"\nCommand failed: {str(e)}")
            else:
                print("\nExecuting default test commands:")
                print("- Hostname:")
                hostname = cls.execute_remote_command(client, "hostname")
                print(f"  Host: {hostname}")
                
                print("- Current directory:")
                pwd = cls.execute_remote_command(client, "pwd")
                print(f"  Directory: {pwd}")
            
            print("\nConnection test successful!")
            cls.close_connection(client)
            return True
            
        except Exception as e:
            print(f"\nConnection test failed: {e}")
            cls.close_connection(client)
            return False