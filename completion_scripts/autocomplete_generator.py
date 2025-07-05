#!/usr/bin/env python
"""
To generate the completion scripts, run the following commands:
```bash
python3 completion_scripts/autocomplete_generator.py --zsh > src/pieces/completions/zsh
python3 completion_scripts/autocomplete_generator.py --bash > src/pieces/completions/bash
python3 completion_scripts/autocomplete_generator.py --fish > src/pieces/completions/fish
python3 completion_scripts/autocomplete_generator.py --powershell > src/pieces/completions/powershell
```

To try it run:

```bash
source <(python3 completion_scripts/autocomplete_generator.py --bash)
```

```zsh
source <(python3 completion_scripts/autocomplete_generator.py --zsh)
```

```fish
python3 completion_scripts/autocomplete_generator.py --fish | source
```

```powershell
python3 completion_scripts/autocomplete_generator.py --powershell | Invoke-Expression
```
"""

import sys
from pieces.app import PiecesCLI
from base import CommandParser
from bash import BashCompletionGenerator
from zsh import ZshCompletionGenerator
from fish import FishCompletionGenerator
from powershell import PowerShellCompletionGenerator
import signal


cli = PiecesCLI()
parser = CommandParser(cli.parser)

if hasattr(signal, "SIGPIPE"):
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def generate(shell_arg):
    try:
        generators = {
            "bash": BashCompletionGenerator,
            "zsh": ZshCompletionGenerator,
            "fish": FishCompletionGenerator,
            "powershell": PowerShellCompletionGenerator,
        }[shell_arg]

        generator = generators(parser, "pieces")
        print(generator.generate())
        sys.exit(0)
    except Exception as e:
        import traceback

        traceback.print_exc()
        print(f"Error generating {shell_arg} completion: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point for the script."""
    if len(sys.argv) >= 2:
        shell_arg = sys.argv[1].lstrip("-")

        if shell_arg in ["bash", "zsh", "fish", "powershell"]:
            generate(shell_arg)
    else:
        print("Usage: python autocomplete_generator.py [--bash|--zsh|--fish|--powershell]")
        print("Generates shell completion scripts for the Pieces CLI")


if __name__ == "__main__":
    main()
