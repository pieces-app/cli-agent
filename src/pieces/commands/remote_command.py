from pieces.settings import Settings
import paramiko
from typing import Optional, Dict, Any

class RemoteCommand:
    @classmethod
    def setup_remote_connection(cls, host: str, username: str, 
                               password: Optional[str] = None, 
                               key_file: Optional[str] = None) -> 'paramiko.SSHClient':
        """
        Set up an SSH connection to a remote host.
        
        Args:
            host: The remote host IP or hostname
            username: The username for SSH connection
            password: Optional password for authentication
            key_file: Optional path to SSH private key file
            
        Returns:
            A configured SSHClient instance
        """
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
        """
        Execute a command on a remote host.
        
        Args:
            client: The SSHClient instance
            command: The command to execute
            
        Returns:
            Dictionary containing stdout and stderr
        """
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
        """
        Close the SSH connection.
        
        Args:
            client: The SSHClient instance to close
        """
        client.close()