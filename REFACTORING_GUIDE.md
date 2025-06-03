# Pieces CLI Command Refactoring Guide

## Overview

This refactoring introduces a new object-oriented command architecture that provides better organization, enhanced metadata support, and easier extensibility for the Pieces CLI.

## Architecture Components

### 1. BaseCommand Class (`src/pieces/base_command.py`)

The foundation of the new architecture. Every command inherits from this abstract base class:

```python
class BaseCommand(ABC):
    """Base class for all CLI commands with enhanced metadata support."""
```

#### Key Methods:
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
4. Register it in `src/pieces/app_refactored.py`:

```python
def _register_commands(self):
    # ...
    self.registry.register(MyCommand())
```

## Benefits of the New Architecture

1. **Enhanced Metadata**: Each command now has dedicated fields for examples, documentation links, and detailed descriptions
2. **Better Organization**: Commands are self-contained classes with clear responsibilities
3. **Easier Testing**: Commands can be tested in isolation
4. **Consistent Interface**: All commands follow the same pattern
5. **Better Documentation**: Examples and docs are part of the command definition
6. **Type Safety**: Better type hints throughout the codebase

## Migration Path

The refactored commands currently wrap the existing command implementations to maintain backward compatibility. This allows for gradual migration:

1. Phase 1: Use new command classes that wrap existing functions (current state)
2. Phase 2: Gradually move logic from old functions into the new command classes
3. Phase 3: Remove old command files once migration is complete

## Examples

### Simple Command (Version)
```python
class VersionCommand(BaseCommand):
    # Minimal implementation with no arguments
```

### Command with Arguments (List)
```python
class ListCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("type", choices=["materials", "apps", "models"])
        parser.add_argument("--editor", action="store_true")
```

### Command Group (MCP)
```python
class MCPCommandGroup(CommandGroup):
    def _register_subcommands(self):
        self.add_subcommand(MCPSetupCommand())
        self.add_subcommand(MCPListCommand())
```

## Running the Refactored CLI

To test the refactored version:

```python
python src/pieces/app_refactored.py [command] [options]
```

The refactored app maintains full compatibility with existing command syntax while providing the enhanced architecture benefits. 