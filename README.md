# Pieces Python CLI Tool

<p align="center"> This is a comprehensive command-line interface (CLI) tool designed to interact seamlessly with PiecesOS. It provides a range of functionalities such as asset management, application interaction, and integration with various PiecesOS features.

</p>
  
##### <p align="center"> [Website](https://pieces.app/) • [PiecesOS Documentation](https://docs.pieces.app/) • [Pieces CLI Documentation](https://docs.pieces.app/extensions-plugins/cli)
</p>

[![Introducing CLI](https://img.youtube.com/vi/kAgwHMxWY8c/0.jpg)](https://www.youtube.com/watch?v=kAgwHMxWY8c)

## Table of Contents

- [Important](#important)
- [Installing](#installing)  
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Available Commands](#available-commands)
  - [📋 Core Material Management](#-core-material-management)
  - [🤖 AI & Copilot Chat](#-ai--copilot-chat)
  - [⚙️ Configuration & Setup](#️-configuration--setup)
  - [🔧 Development Tools](#-development-tools)
  - [🔌 MCP Integration](#-mcp-integration)
  - [🛠️ System & Setup](#️-system--setup)
- [🎥 Video Tutorials & Demonstrations](#-video-tutorials--demonstrations)
- [Contributing](#contributing)

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

### Quick Start

1. **First Time Setup**: Run the onboarding process
   ```bash
   pieces onboarding
   ```

2. **Check Status**: Verify PiecesOS is running
   ```bash
   pieces version
   ```

3. **Explore Your Materials**: List existing materials
   ```bash
   pieces list
   ```

4. **Start Chatting with AI**: Ask your first question
   ```bash
   pieces ask "How do I get started with Pieces CLI?"
   ```

5. **Set Up IDE Integration**: Connect with your favorite editor
   ```bash
   # For VS Code users
   pieces mcp setup --vscode --globally
   
   # For Cursor users  
   pieces mcp setup --cursor --globally
   ```

### Important Terminologies

- **Material**: A code snippet, file, or piece of content saved in Pieces
- **Current Asset**: The material you are currently working with (changeable via `pieces list --editor`)
- **Current Conversation**: The active chat session used in ask commands
- **MCP Integration**: Model Context Protocol connection between Pieces and your IDE
- **LTM**: Long Term Memory - AI context awareness of your development history

## Usage

The Pieces CLI provides extensive functionality through intuitive commands. All commands include built-in help:

```bash
# General help
pieces --help

# Command-specific help  
pieces ask --help
pieces mcp setup --help
```

For comprehensive command documentation with examples, see the **Available Commands** section below. For the most up-to-date command reference, visit the [official documentation](https://docs.pieces.app/extensions-plugins/cli/commands).

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

The Pieces CLI provides a comprehensive set of commands organized by functionality. Use `pieces <command> --help` for detailed help on any specific command.

### 📋 Core Material Management

#### `pieces list` (alias: `drive`)
List and manage your materials, applications, or AI models.

```bash
# List materials (default, shows 10 most recent)
pieces list
# or
pieces drive

# List with custom count
pieces list materials 20

# List applications
pieces list apps

# List AI models
pieces list models

# Open selected material in editor
pieces list --editor
```

#### `pieces create`
Create a new material from clipboard or specified content.

```bash
# Create from clipboard
pieces create

# Create with custom content
pieces create --content
```

#### `pieces save` (alias: `modify`)
Update the current material with changes.

```bash
pieces save
# or
pieces modify
```

#### `pieces delete`
Delete the current or specified material.

```bash
pieces delete
```

#### `pieces edit`
Edit material properties like name or classification.

```bash
# Edit material name
pieces edit --name "New Material Name"

# Reclassify material
pieces edit --classification "python"

# Edit both
pieces edit --name "Updated Script" --classification "bash"
```

#### `pieces share`
Share the current material.

```bash
pieces share
```

#### `pieces execute`
Execute shell or bash materials directly.

```bash
pieces execute
```

#### `pieces search`
Search through your materials with different modes.

```bash
# Fuzzy search (default)
pieces search "python function"

# Neural code search
pieces search "authentication logic" --mode ncs

# Full text search
pieces search "database connection" --mode fts
```

### 🤖 AI & Copilot Chat

#### `pieces ask`
Ask questions to the Pieces Copilot with contextual awareness.

```bash
# Simple question
pieces ask "How do I implement a REST API in Python?"

# Ask with file context
pieces ask "Explain this code" --files ./src/main.py

# Ask with material context
pieces ask "Improve this function" --materials 1 3 5

# Ask with LTM (Long Term Memory) enabled
pieces ask "What was I working on yesterday?" --ltm
```

#### `pieces chat` (alias: `conversation`)
Manage and navigate chat conversations.

```bash
# Show current chat messages
pieces chat
# or 
pieces conversation

# Switch to specific chat by index
pieces chat 2

# Create new chat
pieces chat --new

# Rename current chat
pieces chat --rename "API Development Discussion"

# Let AI rename the chat based on context
pieces chat --rename

# Delete current chat
pieces chat --delete
```

#### `pieces chats` (alias: `conversations`)
List all chat conversations with preview.

```bash
# List recent chats (default: 10)
pieces chats
# or
pieces conversations

# List more chats
pieces chats 25
```

### ⚙️ Configuration & Setup

#### `pieces config`
View and modify CLI configuration.

```bash
# View current config
pieces config

# Set default editor
pieces config --editor code
pieces config --editor vim
```

#### `pieces login` / `pieces logout`
Authenticate with Pieces services.

```bash
# Login to Pieces
pieces login

# Logout from Pieces
pieces logout
```

#### `pieces version`
Display version information for PiecesOS and CLI.

```bash
pieces version
```

### 🔧 Development Tools

#### `pieces commit`
Auto-generate commit messages and commit changes.

```bash
# Generate commit message and commit
pieces commit

# Commit and push to remote
pieces commit --push

# Stage all files before committing
pieces commit --all

# Include issue numbers in commit message
pieces commit --issues
```

#### `pieces run`
Start an interactive CLI loop for continuous usage.

```bash
pieces run
```

### 🔌 MCP Integration

The Model Context Protocol (MCP) integration allows Pieces to work seamlessly with various IDEs and AI tools.

#### `pieces mcp setup`
Set up MCP integration for your preferred development environment.

**VS Code Setup:**
```bash
# Set up globally for all workspaces
pieces mcp setup --vscode --globally

# Set up for specific workspace
pieces mcp setup --vscode --specific-workspace
```

**Cursor Setup:**
```bash
# Set up globally for all workspaces
pieces mcp setup --cursor --globally

# Set up for specific workspace
pieces mcp setup --cursor --specific-workspace
```

**Other IDEs:**
```bash
# Set up for Goose
pieces mcp setup --goose

# Set up for Claude Desktop
pieces mcp setup --claude

# Use stdio instead of SSE
pieces mcp setup --cursor --stdio
```

#### `pieces mcp list`
View MCP integration status.

```bash
# List already registered MCPs
pieces mcp list --already-registered

# List available MCPs ready for setup
pieces mcp list --available-for-setup
```

#### `pieces mcp docs`
Access integration documentation.

```bash
# Show all documentation
pieces mcp docs

# Show specific IDE docs
pieces mcp docs --ide cursor
pieces mcp docs --ide vscode
pieces mcp docs --ide goose
pieces mcp docs --ide claude

# Open documentation in browser
pieces mcp docs --ide cursor --open
```

#### `pieces mcp repair`
Fix MCP configuration issues.

```bash
# Repair all integrations
pieces mcp repair

# Repair specific IDE
pieces mcp repair --ide cursor
pieces mcp repair --ide vscode
```

#### `pieces mcp status`
Check the status of LTM and MCP integrations.

```bash
pieces mcp status
```

#### `pieces mcp start`
Start the stdio MCP server.

```bash
pieces mcp start
```

### 🛠️ System & Setup

#### `pieces install`
Install PiecesOS (required for CLI functionality).

```bash
pieces install
```

#### `pieces open`
Open Pieces applications and interfaces.

```bash
# Open PiecesOS
pieces open --pieces_os

# Open Pieces Copilot
pieces open --copilot

# Open Pieces Drive
pieces open --drive

# Open Pieces Settings
pieces open --settings
```

#### `pieces onboarding`
Start the interactive onboarding process.

```bash
pieces onboarding
```

#### `pieces feedback`
Submit feedback to the Pieces team.

```bash
pieces feedback
```

#### `pieces contribute`
Learn how to contribute to Pieces CLI development.

```bash
pieces contribute
```

#### `pieces help`
Display help information.

```bash
pieces help
```

## 🎥 Video Tutorials & Demonstrations

*Coming Soon: Video recordings demonstrating key CLI features*

### Critical Workflows
- **MCP Setup Tutorial**: Step-by-step guide for setting up MCP integration with VS Code, Cursor, and other IDEs
- **Copilot Chat Demo**: Interactive demonstration of AI-powered conversations with contextual awareness
- **Material Management**: Complete workflow for creating, organizing, and sharing code materials
- **Search & Discovery**: Advanced search techniques using different modes (fuzzy, neural, full-text)

### Quick Start Videos
- **5-Minute Setup**: From installation to first AI conversation
- **Daily Developer Workflow**: Real-world usage patterns and productivity tips
- **Integration Showcase**: Seamless workflow with popular development tools

*Note: Video links will be added as content becomes available*
