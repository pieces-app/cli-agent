# Pieces Python CLI Tool

<p align="center"> This is a comprehensive command-line interface (CLI) tool designed to interact seamlessly with PiecesOS. It provides a range of functionalities such as asset management, application interaction, and integration with various PiecesOS features.

</p>
  
##### <p align="center"> [Website](https://pieces.app/) • [PiecesOS Documentation](https://docs.pieces.app/) • [Pieces CLI Documentation](https://docs.pieces.app/extensions-plugins/cli)
</p>

[![Introducing CLI](https://img.youtube.com/vi/kAgwHMxWY8c/0.jpg)](https://www.youtube.com/watch?v=kAgwHMxWY8c)

## Important

Make sure you have [**PiecesOS**](https://docs.pieces.app/products/meet-pieces/fundamentals) installed in order to run the Pieces CLI tool.

#### Operating System Support

The Pieces Python CLI Tool is compatible with various operating systems, ensuring a wide range of usage and adaptability. While it offers full support across most systems, specific features might have varied performance based on the OS environment.

The CLI Supports

- Windows 10 or greater
- Mac
- Windows

## Installing

To get started with the Pieces Python CLI Tool, you need to:

1. Ensure PiecesOS is installed and running on your system.
2. Install the Python package:

   ```bash
   pip install pieces-cli
   ```

   ```bash
   brew install pieces-cli
   ```

   ```bash
   conda install pieces-cli
   ```

## Getting Started

After installing the CLI tool, you can access its functionalities through the terminal. The tool is initialized with the command `pieces` followed by various subcommands and options.

### Some important terminologies

- `x` -> The index
- `current asset` -> The asset that you are currently using can be changed by the open command
- `current conversation` -> The conversation that you currently using in the ask command

## Shell Completion

The Pieces CLI supports auto-completion for bash, zsh, fish, and PowerShell. To enable completion for your shell, run:

```bash
pieces completion [shell]
```

**Quick setup commands for each shell:**

- **Bash:**
```bash
echo 'eval "$(pieces completion bash)"' >> ~/.bashrc && source ~/.bashrc
```

- **Zsh:**
```zsh
echo 'eval "$(pieces completion zsh)"' >> ~/.zshrc && source ~/.zshrc
```

- **Fish:**
```fish
echo 'pieces completion fish | source' >> ~/.config/fish/config.fish && source ~/.config/fish/config.fish
```

- **PowerShell:**
```powershell
Add-Content $PROFILE '$completionPiecesScript = pieces completion powershell | Out-String; Invoke-Expression $completionPiecesScript'; . $PROFILE
```

After setup, restart your terminal or source your configuration file. Then try typing `pieces ` and press **Tab** to test auto-completion!

## Usage

To refer to the list of all the commands currently supported in the Pieces CLI Agent, visit the [documentation](https://docs.pieces.app/extensions-plugins/cli/commands).

## Contributing

### Installation

To run this project locally, follow these steps:

1. Fork this project via GitHub.

2. Clone this project:

```shell
git clone https://github.com/pieces-app/cli-agent
```

3. Create a Virtual Environment

```shell
python3 -m venv venv
```

4. Activate Your Virtualenv

```shell
source venv/bin/activate for Mac & Linux OS

cd venv\Scripts for Windows OS
activate
```

5. This project uses poetry for managing dependencies and builds. Install poetry with:

```shell
pip install poetry
```

6. Then use poetry to install the required dependencies

```shell
poetry install
```

7. You build with

```shell
poetry build
```

8. Finally any project dependencies should be added to the pyproject.toml file with

```shell
poetry add
```

9. Open the Dist folder

```shell
cd dist
```

10. Install the WHL file

```shell
pip install pieces-cli-{VERSION}-py3-none-any.whl
```

replace the VERSION with the version you downloaded
Note: Ensure you get latest from the [releases](https://github.com/pieces-app/cli-agent/releases) of the cli-agent

11. To view all the CLI Commands

```shell
pieces help
```

these can be local/github/pypi etc.

### Updating

To update the project, run the following command:

```shell
pip install pieces-cli --upgrade
```

### Testing

To discover and run all the test cases in the repository, run the following command:

```shell
pytest
```

To check the test coverage, you can use the coverage package. Install coverage with:

```shell
pip install coverage
```

Run the tests with coverage using the following command:

```shell
coverage run -m pytest
coverage report
```

### Uninstallation

To uninstall the project, run the following command:

```shell
pip uninstall pieces-cli
```

Don't forget to remove the virtual environment and dist folder

## Available Commands

```
  run               - Starts a looped version of the CLI that only requires you to type the flag

  list              - Lists all the materials in your Pieces Drive (alias: 'drive')
  list apps         - List all registered applications
  list models       - List all registered AI models and change the AI model that you are using the ask command

  modify            - Modify the current material content after you edit it in the editor
  edit              - Edit the current material name or classification you can use -n and -c for name and classification respectively
  delete            - Deletes the current or most recent material.
  create            - Creates a new material based on what you've copied to your clipboard
  execute           - Execute a Pieces bash material
  clear             - to clear the terminal

  config            - View current configuration
  config --editor x - Set the editor to 'x' in the configuration

  ask "ask"       - Asks a single question to the model selected in change model. Default timeout set to 10 seconds
  --materials,-m    - Add material(s) by index. Separate materials with spaces. Run 'drive' to find material indexes
  --file,-f         - Add a certain files or folders to the ask command it can be absolute or relative path

  chats             - List all the chats. The green chat shows the currently using one in the ask command
  chat              - Show the messages of the currently using chat in the ask command
  chat x            - List all the messages in a certain chat and switch to it in the ask command
  -n,--new          - To create a new chat in the ask command
  -d,--delete       - Deletes the current chat
  -r,--rename       - Rename the current chat. If no value given it will let the model rename it for you

  commit            - Commits the changes to github and auto generate the message, you can use -p or --push to push

  search q          - Does a fuzzy search for your query
  --mode ncs        - Does a neural code search for your query
  --mode fts        - Does a full text search for your query

  login             - Login to pieces
  logout            - Logout from pieces

  version           - Gets version of PiecesOS and the version of the cli tool
  help              - Show this help message
  onboarding        - Start the onboarding process
  feedback          - Send feedback to Pieces
  contribute        - Contribute to Pieces CLI
  install           - Install PiecesOS
  open              - Opens PiecesOS
```
