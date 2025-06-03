"""
Documentation Generator for Pieces CLI Commands

This should be added to the CI/CD pipeline to generate the documentation for the CLI commands.
"""

import os
import sys
import inspect
import argparse
from typing import List, Dict, Any
from pathlib import Path

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from pieces.base_command import BaseCommand, CommandGroup
from pieces.command_registry import CommandRegistry
from pieces.pieces_argparser import PiecesArgparser
from pieces.command_interface import *


class DocsGenerator:
    """Generates documentation for CLI commands."""

    def __init__(self, output_file: str = "DOCS.md"):
        self.output_file = output_file
        self.commands_info = []

    def extract_command_info(self, command: BaseCommand) -> Dict[str, Any]:
        """Extract comprehensive information from a command."""
        info = {
            "name": command.name,
            "aliases": command.aliases,
            "help": command.help,
            "description": command.description,
            "examples": command.examples,
            "docs_url": command.docs,
            "arguments": [],
            "is_group": isinstance(command, CommandGroup),
            "subcommands": [],
        }

        # Extract arguments by creating a temporary parser
        try:
            temp_parser = argparse.ArgumentParser(prog=f"pieces {command.name}")
            command.add_arguments(temp_parser)

            # Extract argument information
            for action in temp_parser._actions:
                if action.dest != "help":  # Skip help action
                    arg_info = {
                        "option_strings": action.option_strings,
                        "dest": action.dest,
                        "help": action.help or "",
                        "required": getattr(action, "required", False),
                        "default": getattr(action, "default", None),
                        "choices": getattr(action, "choices", None),
                        "type": getattr(action, "type", str).__name__
                        if hasattr(action, "type") and action.type
                        else "str",
                        "nargs": getattr(action, "nargs", None),
                    }
                    info["arguments"].append(arg_info)
        except Exception as e:
            print(f"Warning: Could not extract arguments for {command.name}: {e}")

        # Extract subcommands if it's a command group
        if isinstance(command, CommandGroup):
            for sub_name, subcommand in command.subcommands.items():
                if sub_name == subcommand.name:  # Skip aliases
                    sub_info = self.extract_command_info(subcommand)
                    info["subcommands"].append(sub_info)

        return info

    def collect_all_commands(self):
        """Collect all registered commands."""
        print("Collecting command information...")

        # Get all unique commands from BaseCommand.commands
        seen_commands = set()
        for command in BaseCommand.commands:
            if command not in seen_commands:
                seen_commands.add(command)
                try:
                    cmd_info = self.extract_command_info(command)
                    self.commands_info.append(cmd_info)
                    print(f"  - Processed: {cmd_info['name']}")
                except Exception as e:
                    print(
                        f"  - Error processing {getattr(command, 'name', 'unknown')}: {e}"
                    )

        # Sort commands alphabetically
        self.commands_info.sort(key=lambda x: x["name"])

    def format_arguments_table(self, arguments: List[Dict]) -> str:
        """Format arguments as a markdown table."""
        if not arguments:
            return "_No arguments_\n"

        table = "| Argument | Type | Required | Default | Description |\n"
        table += "|----------|------|----------|---------|-------------|\n"

        for arg in arguments:
            option_str = (
                ", ".join(arg["option_strings"])
                if arg["option_strings"]
                else arg["dest"]
            )
            arg_type = arg["type"]
            required = "✓" if arg["required"] else ""
            default = str(arg["default"]) if arg["default"] is not None else ""
            description = arg["help"].replace("|", "\\|")  # Escape pipes for markdown

            table += f"| `{option_str}` | {arg_type} | {required} | {default} | {description} |\n"

        return table + "\n"

    def format_examples(self, examples: List[str]) -> str:
        """Format examples as markdown code blocks."""
        if not examples:
            return "_No examples available_\n"

        formatted = ""
        for example in examples:
            formatted += f"```bash\n{example}\n```\n\n"

        return formatted

    def generate_command_section(self, cmd_info: Dict[str, Any], level: int = 2) -> str:
        """Generate markdown section for a single command."""
        header_prefix = "#" * level
        section = f"{header_prefix} {cmd_info['name']}\n\n"

        # Add aliases if any
        if cmd_info["aliases"]:
            aliases_str = ", ".join([f"`{alias}`" for alias in cmd_info["aliases"]])
            section += f"**Aliases:** {aliases_str}\n\n"

        # Add description
        section += f"{cmd_info['description']}\n\n"

        # Add documentation URL if available
        if cmd_info["docs_url"]:
            section += f"**Documentation:** [{cmd_info['docs_url']}]({cmd_info['docs_url']})\n\n"

        # Add usage examples
        section += f"{header_prefix}# Examples\n\n"
        section += self.format_examples(cmd_info["examples"])

        # Add arguments
        section += f"{header_prefix}# Arguments\n\n"
        section += self.format_arguments_table(cmd_info["arguments"])

        # Add subcommands if any
        if cmd_info["subcommands"]:
            section += f"{header_prefix}# Subcommands\n\n"
            for subcommand in cmd_info["subcommands"]:
                section += self.generate_command_section(subcommand, level + 1)

        return section

    def generate_table_of_contents(self) -> str:
        """Generate a table of contents for all commands."""
        toc = "## Table of Contents\n\n"

        for cmd_info in self.commands_info:
            toc += (
                f"- [{cmd_info['name']}](#{cmd_info['name'].lower().replace(' ', '-')})"
            )
            if cmd_info["aliases"]:
                aliases_str = ", ".join(cmd_info["aliases"])
                toc += f" (aliases: {aliases_str})"
            toc += "\n"

            # Add subcommands to TOC
            if cmd_info["subcommands"]:
                for subcommand in cmd_info["subcommands"]:
                    toc += f"  - [{subcommand['name']}](#{subcommand['name'].lower().replace(' ', '-')})\n"

        return toc + "\n"

    def generate_docs(self):
        """Generate the complete documentation."""
        print(f"Generating documentation to {self.output_file}...")

        # Collect all commands
        self.collect_all_commands()

        # Generate documentation content
        content = "# Pieces CLI Command Documentation\n\n"
        content += "This document contains comprehensive documentation for all Pieces CLI commands.\n\n"
        content += f"_Generated automatically from command definitions_\n\n"

        # Add table of contents
        content += self.generate_table_of_contents()

        # Add command sections
        for cmd_info in self.commands_info:
            content += self.generate_command_section(cmd_info)
            content += "---\n\n"  # Separator between commands

        # Add footer
        content += "## Additional Information\n\n"
        content += "For more information about Pieces CLI, visit:\n"
        content += (
            "- [Pieces CLI Repository](https://github.com/pieces-app/cli-agent)\n"
        )
        content += "- [Pieces Documentation](https://docs.pieces.app/)\n"
        content += "- [Pieces Website](https://pieces.app/)\n"

        # Write to file
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"Documentation generated successfully!")
        print(f"  - Commands documented: {len(self.commands_info)}")
        print(f"  - Output file: {self.output_file}")


def main():
    """Main entry point for the documentation generator."""
    parser = argparse.ArgumentParser(
        description="Generate documentation for Pieces CLI commands"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="DOCS.md",
        help="Output file for the generated documentation (default: DOCS.md)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )

    args = parser.parse_args()

    try:
        generator = DocsGenerator(output_file=args.output)
        generator.generate_docs()

    except Exception as e:
        print(f"Error generating documentation: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
