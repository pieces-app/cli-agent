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

## Accessibility

The Pieces CLI supports accessibility features to ensure it's usable for everyone, including users with visual impairments and those who prefer accessible interfaces.

### NO_COLOR Support

The CLI respects the `NO_COLOR` environment variable as specified in the [no-color.org](https://no-color.org/) standard. When this variable is set (regardless of its value), the CLI will suppress all colored output.

```bash
# Disable colors
export NO_COLOR=1
pieces list
```

### Color Schemes

The CLI supports multiple color schemes for different accessibility needs:

- **default**: Standard color scheme
- **high_contrast**: High contrast mode for low vision users
- **monochrome**: No colors, uses text indicators (✓, ✗, ⚠)
- **deuteranopia**: Red-green colorblind friendly
- **protanopia**: Red-green colorblind friendly
- **tritanopia**: Blue-yellow colorblind friendly

```bash
# Set color scheme
export PIECES_COLOR_SCHEME=high_contrast
pieces list
```

### Text Indicators

When colors are disabled (via `NO_COLOR` or monochrome scheme), the CLI adds text indicators to preserve semantic meaning:

- ✓ Success messages
- ✗ Error messages
- ⚠ Warning messages
- ℹ Information messages

### System Integration

The CLI automatically detects system accessibility preferences:
- Windows high contrast mode
- Standard NO_COLOR environment variable
- Custom color scheme preferences

### Screen Reader Support

The CLI provides enhanced support for screen readers to ensure accessibility for users with visual impairments.

#### Screen Reader Detection

The CLI automatically detects common screen readers:
- **Environment Variables**: `PIECES_SCREEN_READER`, `SCREEN_READER`, `JAWS`, `NVDA`, `ORCA`, `VOICEOVER`, `TALKBACK`
- **Platform Detection**: Windows registry checks for JAWS/NVDA, macOS VoiceOver status, Linux Orca process

```bash
# Manually enable screen reader mode
export PIECES_SCREEN_READER=1
pieces list
```

#### Screen Reader Optimizations

When screen reader mode is enabled, the CLI:
- Removes visual-only formatting (box drawing characters, decorative symbols)
- Uses descriptive text indicators instead of Unicode symbols
- Adds spoken-friendly prefixes (e.g., "Success:", "Error:", "Warning:")
- Provides extra spacing for better content separation
- Simplifies complex table/structure layouts

#### Verbose Mode

Verbose mode provides more descriptive output that's helpful for screen readers and users who prefer detailed information.

```bash
# Enable verbose mode
export PIECES_VERBOSE=1
pieces list
```

Verbose mode is automatically enabled when screen reader mode is detected.

#### Screen Reader Friendly Output

The CLI provides specialized output methods for screen readers:
- **Structured Data**: Numbered lists with clear separators
- **Progress Information**: Spoken percentages and descriptive progress
- **List Display**: Item-by-item announcement with numbering

### Keyboard Navigation

The CLI provides enhanced keyboard navigation features for users who prefer keyboard-only interaction or require keyboard accessibility.

#### Keyboard Navigation Mode

Keyboard navigation mode can be enabled via environment variable or is automatically enabled when screen reader mode is detected.

```bash
# Manually enable keyboard navigation
export PIECES_KEYBOARD_NAVIGATION=1
pieces list
```

#### Keyboard Navigation Features

When keyboard navigation is enabled, the CLI provides:
- **Keyboard Shortcuts**: Quick access to common actions
- **Numbered Menus**: Easy selection using number keys (1-9, then a-z)
- **Shortcut Hints**: Visual indicators for keyboard commands
- **Menu Navigation**: Keyboard-friendly menu layouts
- **Focus Management**: Clear focus indicators for interactive elements

#### Default Keyboard Shortcuts

The CLI includes default keyboard shortcuts:
- `q` - Quit/Exit
- `?` - Show help
- `h` - Go to home

#### Reduced Motion

For users who prefer reduced motion or have vestibular disorders, the CLI supports reduced motion mode.

```bash
# Enable reduced motion
export PIECES_REDUCED_MOTION=1
pieces list
```

When reduced motion is enabled:
- Animations and transitions are disabled
- Progress bars use simple text format instead of visual bars
- Dynamic content changes are immediate without transitions
- System reduced motion preferences are automatically detected (Windows, macOS, Linux)

### Cognitive Accessibility

The CLI provides cognitive accessibility features to help users process information more easily and understand complex technical messages.

#### Simplified Output Mode

Simplified output reduces complexity and makes information easier to process.

```bash
# Enable simplified output
export PIECES_SIMPLIFIED_OUTPUT=1
pieces list
```

When simplified output is enabled:
- Large lists are truncated to reduce cognitive load
- Progress information uses descriptive terms (e.g., "about halfway done" instead of "50%")
- Debug information and stack traces are removed from error messages
- Technical details are minimized

Simplified output is automatically enabled when screen reader mode is detected.

#### Clear Language Mode

Clear language mode uses simpler words and provides more context to help users understand technical information.

```bash
# Enable clear language
export PIECES_CLEAR_LANGUAGE=1
pieces list
```

When clear language is enabled:
- Technical jargon is replaced with everyday language (e.g., "execute" → "run", "configuration" → "settings")
- Error messages are translated into clear, actionable guidance
- Command descriptions use simple, plain language
- Confirmation prompts are more direct and clear
- Context-aware help provides simple, actionable suggestions

Clear language is automatically enabled when simplified output is enabled.

#### Error Message Simplification

The CLI automatically simplifies technical error messages into clear language:

- "Connection refused" → "Cannot connect to the service. Please check if PiecesOS is running."
- "Authentication failed" → "Could not verify your identity. Please check your login credentials."
- "Permission denied" → "You don't have permission to do this. Please check your access rights."

#### Context-Aware Help

When errors occur, the CLI provides context-aware help suggestions in simple language:
- Network errors: Suggest checking internet connection
- Permission errors: Suggest checking login status
- File errors: Suggest verifying file existence and access

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
