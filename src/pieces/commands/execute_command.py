from pieces.settings import Settings
from .assets_command import check_assets_existence, AssetsCommands
import subprocess
from pieces.utils import PiecesSelectMenu
from pieces_os_client.models.classification_specific_enum import ClassificationSpecificEnum
from .remote_command import RemoteCommand

class ExecuteCommand:
    @classmethod
    @check_assets_existence
    def execute_command(cls, **kwargs):
        assets = [
            (f"{asset.name}", {"asset_id": asset.id,  "asset": asset})
            for i, asset in enumerate(list(Settings.pieces_client.assets()),
                                      start=1)
            if asset.classification in (ClassificationSpecificEnum.SH,
                                        ClassificationSpecificEnum.BAT)
        ]

        if not assets:
            print("No shell or bash assets found")
            return

        def open_and_execute_asset(**kwargs):
            AssetsCommands.open_asset(**kwargs)
            cls.execute_asset(**kwargs)

        select_menu = PiecesSelectMenu(assets, open_and_execute_asset)
        select_menu.run()

    @classmethod
    def execute_asset(cls, **kwargs):
        asset = kwargs["asset"]
        
        try:
            # Get remote config if enabled
            remote_config = RemoteCommand.get_remote_config()
            use_remote = bool(remote_config)

            # Prepare command based on classification
            if asset.classification == ClassificationSpecificEnum.BASH:
                command = ['bash', '-c', asset.raw_content]
                remote_command = f"bash -c '{asset.raw_content}'"
            elif asset.classification == ClassificationSpecificEnum.SH:
                command = asset.raw_content
                remote_command = asset.raw_content
            else:
                raise ValueError(
                    f"Unsupported classification {asset.classification}")

            if use_remote:
                try:
                    # Set up remote connection using saved config
                    client = RemoteCommand.setup_remote_connection(
                        host=remote_config['host'],
                        username=remote_config['username'],
                        password=remote_config.get('password'),
                        key_file=remote_config.get('key_file')
                    )
                    
                    # Execute on remote host
                    result = RemoteCommand.execute_remote_command(client, remote_command)
                    RemoteCommand.close_connection(client)
                    
                    print(f"Executing {asset.classification.value} command on {remote_config['host']}:")
                    print(result['stdout'])
                    if result['stderr']:
                        print("Errors:")
                        print(result['stderr'])
                except Exception as e:
                    print(f"Remote execution failed: {e}")
                    print("Falling back to local execution...")
                    use_remote = False

            # Local execution (either by choice or fallback)
            if not use_remote:
                if isinstance(command, list):
                    result = subprocess.run(command, capture_output=True, text=True)
                else:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                
                print(f"Executing {asset.classification.value} command locally:")
                print(result.stdout)
                if result.stderr:
                    print("Errors:")
                    print(result.stderr)

        except Exception as e:
            print(f"An error occurred: {e}")