## Testing a remote branch locally

1. Clone this repo locally `git clone <repo>`
2. Fetch remote branches `git fetch`
3. Checkout the feature branch `git checkout <feat-branch-name>`
4. Install dependencies `poetry install`
5. Run the CLI with `python src/pieces <CLI command>` (or `python3`)

Ex: `python src/pieces help` or `python src/pieces config --editor vim`

## Testing a staging release

1. Download and unzip the release for your architecture
2. `pip install path/to/download` (or `pip3`)
3. `python -m pieces version` (or `python3`) <-- check you are running the staging version

Ex: `python -m pieces help` or `python -m pieces config --editor vim`

## Release

```
git tag <tagname>
git push origin <tagname>
```

## Architecture Components

### 1. BaseCommand Class (`src/pieces/base_command.py`)

The foundation of the new architecture. Every command inherits from this abstract base class:

```python
class BaseCommand(ABC):
    """Base class for all CLI commands with enhanced metadata support."""
```

#### Key Methods

- `get_name()`: Returns the primary command name
- `get_aliases()`: Returns alternative names for the command
- `get_help()`: Returns a short help message
- `get_description()`: Returns a detailed description
- `get_examples()`: Returns usage examples
- `get_docs()`: Returns documentation URL
- `add_arguments()`: Adds command-specific arguments to the parser
- `execute()`: Executes the command logic

### 2. CommandGroup Class (`src/pieces/base_command.py`)

For commands that have subcommands (like `mcp`):

```python
class CommandGroup(BaseCommand):
    """Base class for commands that have subcommands."""
```

### 3. CommandRegistry (`src/pieces/command_registry.py`)

Manages all registered commands and integrates with the PiecesArgparser:

```python
class CommandRegistry:
    """Registry for managing all CLI commands."""
```

## How to Add a New Command

1. Create a new file in `src/pieces/commands_new/`
2. Import and extend `BaseCommand`:

```python
from pieces.base_command import BaseCommand

class MyCommand(BaseCommand):
    def get_name(self) -> str:
        return "mycommand"
    
    def get_help(self) -> str:
        return "Short description"
    
    def get_description(self) -> str:
        return "Detailed description"
    
    def get_examples(self) -> list[str]:
        return ["pieces mycommand", "pieces mycommand --option"]
    
    def get_docs(self) -> str:
        return "https://docs.pieces.app/products/cli#mycommand"
    
    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument("--option", help="An option")
    
    def execute(self, **kwargs) -> int:
        # Command logic here
        return 0  # Return 0 for success
```

3. Export it in `src/pieces/commands_new/__init__.py`
