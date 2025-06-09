import argparse
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
from pieces.app import PiecesCLI
from pieces.base_command import BaseCommand
from pieces import __version__
import sys


class CommandInfo:
    """Data class to hold command information."""

    def __init__(self, name: str, help: str, description: str, aliases: List[str]):
        self.name = name
        self.help = help
        self.description = description
        self.aliases = aliases


class OptionInfo:
    """Data class to hold option information."""

    def __init__(
        self,
        flags: Tuple[str, ...],
        dest: str,
        help: str,
        type: Optional[type] = None,
        nargs: Optional[str] = None,
        choices: Optional[List[Any]] = None,
    ):
        self.flags = flags
        self.dest = dest
        self.help = help or ""
        self.type = type
        self.nargs = nargs
        self.choices = choices

    @property
    def short_flag(self) -> Optional[str]:
        """Get the short flag (e.g., '-f') if it exists."""
        for flag in self.flags:
            if flag.startswith("-") and not flag.startswith("--"):
                return flag[1:]  # Remove the dash
        return None

    @property
    def long_flag(self) -> Optional[str]:
        """Get the long flag (e.g., '--file') if it exists."""
        for flag in self.flags:
            if flag.startswith("--"):
                return flag[2:]  # Remove the dashes
        return None

    def is_file_type(self) -> bool:
        """Check if this option expects file/directory input."""
        return self.dest in ["file", "files", "path", "directory", "folder"]

    def is_integer_type(self) -> bool:
        """Check if this option expects integer input."""
        return self.type is int and self.nargs in ["*", "+", "?"]


class PositionalInfo:
    """Data class to hold positional argument information."""

    def __init__(
        self,
        dest: str,
        help: str,
        type: Optional[type] = None,
        nargs: Optional[str] = None,
        choices: Optional[List[Any]] = None,
    ):
        self.dest = dest
        self.help = help or dest
        self.type = type
        self.nargs = nargs
        self.choices = choices

    def is_file_type(self) -> bool:
        """Check if this positional expects file/directory input."""
        return self.dest in ["file", "files", "path"]


class CommandParser:
    """Parses argparse commands and extracts completion information."""

    def __init__(self, parser: argparse.ArgumentParser):
        self.parser = parser
        self.commands_info: Dict[str, CommandInfo] = {}
        self.aliases_map: Dict[str, str] = {}
        self.subcommand_details: Dict[str, Dict[str, Any]] = {}
        self._parse_commands()
        self._parse_subcommands()

    def _parse_commands(self):
        """Parse commands from BaseCommand registry."""
        for command in BaseCommand.commands:
            cmd_info = CommandInfo(
                name=command.name,
                help=command.help,
                description=command.description,
                aliases=command.aliases,
            )
            self.commands_info[command.name] = cmd_info

            # Map aliases to main command
            for alias in command.aliases:
                self.aliases_map[alias] = command.name

    def _parse_subcommands(self):
        """Parse subcommand details from argparse."""
        subparsers_actions = [
            action
            for action in self.parser._actions
            if isinstance(action, argparse._SubParsersAction)
        ]

        for subparsers_action in subparsers_actions:
            for choice, sub_parser in subparsers_action.choices.items():
                options = []
                positionals = []

                # Check if this subparser has its own subparsers (command group)
                sub_subparsers_actions = [
                    action
                    for action in sub_parser._actions
                    if isinstance(action, argparse._SubParsersAction)
                ]

                if sub_subparsers_actions:
                    # This is a command group, parse its subcommands
                    for sub_subparsers_action in sub_subparsers_actions:
                        for (
                            sub_choice,
                            sub_sub_parser,
                        ) in sub_subparsers_action.choices.items():
                            sub_options = []
                            sub_positionals = []

                            for action in sub_sub_parser._actions:
                                if action.option_strings:
                                    opt_info = OptionInfo(
                                        flags=tuple(action.option_strings),
                                        dest=action.dest,
                                        help=action.help,
                                        type=action.type,
                                        nargs=action.nargs,
                                        choices=action.choices,
                                    )
                                    sub_options.append(opt_info)
                                elif (
                                    action.dest != "help"
                                    and not action.dest.startswith("_")
                                ):
                                    pos_info = PositionalInfo(
                                        dest=action.dest,
                                        help=action.help,
                                        type=action.type,
                                        nargs=action.nargs,
                                        choices=action.choices,
                                    )
                                    sub_positionals.append(pos_info)

                            # Store with parent_subcommand format
                            key = f"{choice}_{sub_choice}"
                            self.subcommand_details[key] = {
                                "options": sub_options,
                                "positionals": sub_positionals,
                            }

                # Also parse the main command's options
                for action in sub_parser._actions:
                    if action.option_strings:
                        # It's an optional argument
                        opt_info = OptionInfo(
                            flags=tuple(action.option_strings),
                            dest=action.dest,
                            help=action.help,
                            type=action.type,
                            nargs=action.nargs,
                            choices=action.choices,
                        )
                        options.append(opt_info)
                    elif (
                        action.dest != "help"
                        and not action.dest.startswith("_")
                        and not isinstance(action, argparse._SubParsersAction)
                    ):
                        # It's a positional argument
                        pos_info = PositionalInfo(
                            dest=action.dest,
                            help=action.help,
                            type=action.type,
                            nargs=action.nargs,
                            choices=action.choices,
                        )
                        positionals.append(pos_info)

                self.subcommand_details[choice] = {
                    "options": options,
                    "positionals": positionals,
                }


class CompletionGenerator(ABC):
    """Abstract base class for shell completion generators."""

    def __init__(self, parser: CommandParser, tool_name: str):
        self.parser = parser
        self.tool_name = tool_name

    @abstractmethod
    def generate(self) -> str:
        """Generate the completion script."""
        pass

    def escape_string(self, text: str) -> str:
        """Escape special characters for the shell."""
        return text.replace('"', '\\"').replace("\n", " ")


class BashCompletionGenerator(CompletionGenerator):
    """Generates Bash completion scripts."""

    def generate(self) -> str:
        """Generate the Bash completion script."""
        script = self._generate_header()
        script += self._generate_main_function()
        script += self._generate_helper_functions()
        script += self._generate_registration()
        return script.strip()

    def _generate_header(self) -> str:
        """Generate the script header."""
        return f"""#!/bin/bash
# Bash completion for {self.tool_name}
# Generated automatically - includes command descriptions and aliases
"""

    def _generate_main_function(self) -> str:
        """Generate the main completion function."""
        all_commands = sorted(
            set(
                list(self.parser.commands_info.keys())
                + list(self.parser.aliases_map.keys())
            )
        )

        script = f"""
_{self.tool_name}_completion() {{
    local cur prev words cword
    _init_completion || return

    local cmd i
    
    # Find the command (first non-option argument after {self.tool_name})
    cmd=""
    for ((i=1; i < cword; i++)); do
        if [[ "${{words[i]}}" != -* ]]; then
            cmd="${{words[i]}}"
            break
        fi
    done

    # Define global options
    local global_options="--help -h --version -v --ignore-onboarding"

    # If we haven't found a command yet, complete with commands
    if [[ -z "$cmd" ]] || [[ "$cword" -eq 1 ]]; then
        # Show commands with descriptions when completing
        if [[ -z "$cur" ]] || [[ "$cur" == -* ]]; then
            # If current word is empty or starts with -, show options
            COMPREPLY=( $(compgen -W "$global_options" -- "$cur") )
        else
            # Show available commands
            local commands="{" ".join(all_commands)}"
            COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
        fi
        return 0
    fi

    # Normalize command (convert alias to main command)
    case "$cmd" in
"""

        # Add alias mappings
        for alias, main_cmd in self.parser.aliases_map.items():
            script += f"""        {alias})
            cmd="{main_cmd}"
            ;;
"""

        script += """    esac

    # Handle command-specific completions
    case "$cmd" in
"""

        # Add command-specific completions
        for cmd_name, cmd_info in self.parser.commands_info.items():
            script += self._generate_command_completion(cmd_name, cmd_info)

        # Add help command
        script += f"""        help)
            # Complete with available commands for help
            local commands="{" ".join(sorted(self.parser.commands_info.keys()))}"
            COMPREPLY=( $(compgen -W "$commands" -- "$cur") )
            return 0
            ;;
"""

        # Default case
        script += """        *)
            # Unknown command, no completion
            return 0
            ;;
    esac
}
"""
        return script

    def _generate_command_completion(self, cmd_name: str, cmd_info: CommandInfo) -> str:
        """Generate completion for a specific command."""
        cmd_details = self.parser.subcommand_details.get(cmd_name, {})
        options = cmd_details.get("options", [])
        positionals = cmd_details.get("positionals", [])

        # Build options string
        option_flags = []
        for opt in options:
            option_flags.extend(opt.flags)
        options_str = " ".join(option_flags)

        script = f"""        {cmd_name})
            # {cmd_info.description}
            local cmd_options="{options_str}"
            
            case "$prev" in
"""

        # Add option-specific completions
        for opt in options:
            if opt.is_file_type():
                for flag in opt.flags:
                    script += f"""                {flag})
                    # Complete with files and directories
                    _filedir
                    return 0
                    ;;
"""
            elif opt.choices:
                choices_str = " ".join(str(c) for c in opt.choices)
                for flag in opt.flags:
                    script += f"""                {flag})
                    # Complete with predefined choices
                    COMPREPLY=( $(compgen -W "{choices_str}" -- "$cur") )
                    return 0
                    ;;
"""
            elif opt.is_integer_type():
                for flag in opt.flags:
                    script += f"""                {flag})
                    # Complete with numeric values
                    COMPREPLY=( $(compgen -W "1 2 3 4 5 6 7 8 9 10" -- "$cur") )
                    return 0
                    ;;
"""

        # Handle positional arguments
        if any(pos.is_file_type() for pos in positionals):
            script += """                *)
                    # Complete with files for positional arguments
                    _filedir
                    return 0
                    ;;
"""
        else:
            script += """                *)
                    # Default option completion
                    COMPREPLY=( $(compgen -W "$cmd_options" -- "$cur") )
                    return 0
                    ;;
"""

        script += """            esac
            ;;
"""
        return script

    def _generate_helper_functions(self) -> str:
        """Generate helper functions."""
        script = f"""
# Helper function to show command descriptions
_{self.tool_name}_describe_commands() {{
    local commands=(
"""

        max_len = max(len(cmd) for cmd in self.parser.commands_info.keys())
        for cmd_name, cmd_info in sorted(self.parser.commands_info.items()):
            description = self.escape_string(cmd_info.help)
            padding = " " * (max_len - len(cmd_name) + 2)
            script += f"""        "{cmd_name}{padding}{description}"
"""

        script += """    )
    
    printf '%s\\n' "${commands[@]}"
}
"""
        return script

    def _generate_registration(self) -> str:
        """Generate completion registration."""
        return f"""
# Register the completion function
complete -F _{self.tool_name}_completion {self.tool_name}

# Also register for common aliases
complete -F _{self.tool_name}_completion pieces-cli
"""


class ZshCompletionGenerator(CompletionGenerator):
    """Generates Zsh completion scripts."""

    def generate(self) -> str:
        """Generate the Zsh completion script."""
        script = self._generate_header()
        script += self._generate_main_function()
        script += self._generate_command_functions()
        script += self._generate_registration()
        return script.strip()

    def _generate_header(self) -> str:
        """Generate the script header."""
        return f"""#compdef {self.tool_name}
# Zsh completion for {self.tool_name}
# Generated automatically - includes command descriptions and aliases
"""

    def _generate_main_function(self) -> str:
        """Generate the main completion function."""
        script = f"""
_{self.tool_name}() {{
    local line state

    _arguments -C \\
        "1: :->cmds" \\
        "*::arg:->args" \\
        "(--help -h){{--help,-h}}'[Show help message]' \\
        "(--version -v){{--version,-v}}'[Show version]' \\
        '--ignore-onboarding[Ignore onboarding for this command]'

    case "$state" in
        cmds)
            _values "commands" \\
"""

        # Add commands with descriptions
        for cmd_name, cmd_info in sorted(self.parser.commands_info.items()):
            description = cmd_info.help.replace("'", "\\'")
            script += f"""                '{cmd_name}[{description}]' \\
"""

        # Add aliases
        for alias, main_cmd in sorted(self.parser.aliases_map.items()):
            description = self.parser.commands_info[main_cmd].help.replace("'", "\\'")
            script += f"""                '{alias}[Alias for {main_cmd}: {description}]' \\
"""

        script = script.rstrip(" \\\n")
        script += """
            ;;
        args)
            case $line[1] in
"""

        # Add command-specific completions
        for cmd_name in self.parser.commands_info.keys():
            script += f"""                {cmd_name})
                    _{self.tool_name}_{cmd_name}
                    ;;
"""

        script += """            esac
            ;;
    esac
}
"""
        return script

    def _generate_command_functions(self) -> str:
        """Generate command-specific completion functions."""
        script = ""

        for cmd_name, cmd_info in self.parser.commands_info.items():
            script += self._generate_command_function(cmd_name, cmd_info)

        return script

    def _generate_command_function(self, cmd_name: str, cmd_info: CommandInfo) -> str:
        """Generate completion function for a specific command."""
        cmd_details = self.parser.subcommand_details.get(cmd_name, {})
        options = cmd_details.get("options", [])
        positionals = cmd_details.get("positionals", [])

        script = f"""
_{self.tool_name}_{cmd_name}() {{
    # Completion for '{cmd_name}' command
    _arguments \\
        '(--help -h){{--help,-h}}'[Show help for {cmd_name}]' \\
"""

        # Add positional arguments
        for i, pos in enumerate(positionals, 1):
            if pos.choices:
                choices = " ".join(str(c) for c in pos.choices)
                script += f"""        '{i}:{{({choices})}}' \\
"""
            elif pos.is_file_type():
                script += f"""        '{i}:{pos.dest}:_files' \\
"""
            else:
                script += f"""        '{i}:{pos.dest}:' \\
"""

        # Add optional arguments
        for opt in options:
            script += self._generate_option_spec(opt)

        # Remove trailing backslash and close
        script = script.rstrip(" \\\n")
        script += "\n}\n"

        return script

    def _generate_option_spec(self, opt: OptionInfo) -> str:
        """Generate Zsh argument specification for an option."""
        if len(opt.flags) == 2:
            short, long = sorted(opt.flags, key=len)
        else:
            short = long = opt.flags[0]

        help_text = opt.help.replace("'", "\\'")

        # Build the argument spec
        if opt.is_file_type():
            if opt.nargs in ["*", "+"]:
                return f"""        '({short} {long})*'{{{short},{long}}}'[{help_text}]:file:_files' \\
"""
            else:
                return f"""        '({short} {long})'{{{short},{long}}}'[{help_text}]:file:_files' \\
"""
        elif opt.choices:
            choices = " ".join(str(c) for c in opt.choices)
            return f"""        '({short} {long})'{{{short},{long}}}'[{help_text}]:choice:({choices})' \\
"""
        elif opt.type == int:
            return f"""        '({short} {long})'{{{short},{long}}}'[{help_text}]:number:' \\
"""
        else:
            # Boolean flags or other options
            if opt.nargs in ["*", "+"]:
                return f"""        '({short} {long})*'{{{short},{long}}}'[{help_text}]' \\
"""
            else:
                return f"""        '({short} {long})'{{{short},{long}}}'[{help_text}]' \\
"""

    def _generate_registration(self) -> str:
        """Generate completion registration."""
        return f"""
# Register the completion
compdef _{self.tool_name} {self.tool_name}
"""


class FishCompletionGenerator(CompletionGenerator):
    """Generates Fish completion scripts."""

    def generate(self) -> str:
        """Generate the Fish completion script."""
        script = self._generate_header()
        script += self._generate_helper_functions()
        script += self._generate_global_options()
        script += self._generate_commands()
        script += self._generate_command_options()
        script += self._generate_command_groups()
        script += self._generate_help_command()
        return script.strip()

    def _generate_header(self) -> str:
        """Generate the script header."""
        return f"""# Fish completion for {self.tool_name}
# This file is automatically generated by the Pieces CLI.
# Do not edit this file manually.
# Version: {__version__}

# Disable file completions by default
complete -c {self.tool_name} -f
"""

    def _generate_helper_functions(self) -> str:
        """Generate Fish helper functions."""
        return f"""
# Helper function to check if we're completing the first argument (command)
function __{self.tool_name}_needs_command
    set -l cmd (commandline -opc)
    set -e cmd[1]  # Remove the program name
    for arg in $cmd
        # If we find a non-option argument, we have a command
        if not string match -q -- '-*' $arg
            return 1
        end
    end
    return 0
end

# Helper function to get the current command
function __{self.tool_name}_get_command
    set -l cmd (commandline -opc)
    set -e cmd[1]  # Remove the program name
    for arg in $cmd
        if not string match -q -- '-*' $arg
            echo $arg
            return 0
        end
    end
    return 1
end

# Helper function to check if we're in a specific command
function __{self.tool_name}_using_command
    set -l cmd (__{self.tool_name}_get_command)
    test "$cmd" = "$argv[1]"
end

# Helper function to check if we need a subcommand for a command group
function __{self.tool_name}_needs_subcommand
    set -l cmd (commandline -opc)
    set -e cmd[1]  # Remove the program name
    set -l command_found 0
    set -l subcommand_found 0
    
    for arg in $cmd
        if not string match -q -- '-*' $arg
            if test $command_found -eq 0
                # This is the main command
                if test "$arg" = "$argv[1]"
                    set command_found 1
                else
                    return 1  # Different command
                end
            else
                # This is a subcommand
                set subcommand_found 1
                return 1
            end
        end
    end
    
    # We found the command but no subcommand yet
    test $command_found -eq 1 -a $subcommand_found -eq 0
end

# Helper function to get the subcommand
function __{self.tool_name}_get_subcommand
    set -l cmd (commandline -opc)
    set -e cmd[1]  # Remove the program name
    set -l command_found 0
    
    for arg in $cmd
        if not string match -q -- '-*' $arg
            if test $command_found -eq 0
                set command_found 1
            else
                # This is the subcommand
                echo $arg
                return 0
            end
        end
    end
    return 1
end

# Helper function to check if we're using a specific subcommand
function __{self.tool_name}_using_subcommand
    set -l main_cmd (__{self.tool_name}_get_command)
    set -l sub_cmd (__{self.tool_name}_get_subcommand)
    test "$main_cmd" = "$argv[1]" -a "$sub_cmd" = "$argv[2]"
end
"""

    def _generate_global_options(self) -> str:
        """Generate global options."""
        return f"""
# Global options
complete -c {self.tool_name} -s h -l help -d "Show help message"
complete -c {self.tool_name} -s v -l version -d "Show version"
complete -c {self.tool_name} -l ignore-onboarding -d "Ignore onboarding for this command"
"""

    def _generate_commands(self) -> str:
        """Generate command completions."""
        script = """
# Commands - only show when no command is specified yet
"""

        # Add main commands
        for cmd_name, cmd_info in sorted(self.parser.commands_info.items()):
            description = cmd_info.help.replace("'", "\\'")
            script += f"""complete -c {self.tool_name} -n "__{self.tool_name}_needs_command" -a "{cmd_name}" -d "{description}"
"""

        # Add aliases
        for alias, main_cmd in sorted(self.parser.aliases_map.items()):
            description = f"Alias for {main_cmd}"
            script += f"""complete -c {self.tool_name} -n "__{self.tool_name}_needs_command" -a "{alias}" -d "{description}"
"""

        return script

    def _generate_command_options(self) -> str:
        """Generate command-specific options."""
        script = """
# Command-specific completions
"""

        for cmd_name, cmd_info in self.parser.commands_info.items():
            script += self._generate_command_completion(cmd_name, cmd_info)

        return script

    def _generate_command_completion(self, cmd_name: str, cmd_info: CommandInfo) -> str:
        """Generate completion for a specific command."""
        script = ""
        cmd_details = self.parser.subcommand_details.get(cmd_name, {})
        options = cmd_details.get("options", [])
        positionals = cmd_details.get("positionals", [])

        # Check if this is a command group
        from pieces.base_command import CommandGroup

        is_command_group = any(
            isinstance(cmd, CommandGroup) and cmd.name == cmd_name
            for cmd in BaseCommand.commands
        )

        if is_command_group:
            # Skip command groups here - they're handled in _generate_command_groups
            return ""

        # For Fish, we need to create separate completion lines for each command/alias
        all_names = [cmd_name] + cmd_info.aliases

        for name in all_names:
            # Use the helper function for condition
            condition = f'"__{self.tool_name}_using_command {name}"'

            # Add options for this command/alias
            for opt in options:
                script += self._generate_option_completion(opt, condition)

            # Add positional arguments for this command/alias
            for pos in positionals:
                script += self._generate_positional_completion(pos, condition)

        return script

    def _generate_option_completion(self, opt: OptionInfo, condition: str) -> str:
        """Generate Fish completion for an option."""
        script = ""

        # Skip help option as it's already defined
        if any("help" in flag for flag in opt.flags):
            return ""

        # Build the completion command
        if opt.is_file_type():
            if opt.short_flag and opt.long_flag:
                script += f"""complete -c {self.tool_name} -n {condition} -s {opt.short_flag} -l {opt.long_flag} -r -F -d "{self.escape_string(opt.help)}"
"""
            elif opt.long_flag:
                script += f"""complete -c {self.tool_name} -n {condition} -l {opt.long_flag} -r -F -d "{self.escape_string(opt.help)}"
"""
        elif opt.choices:
            choices_str = " ".join(str(c) for c in opt.choices)
            if opt.short_flag and opt.long_flag:
                script += f"""complete -c {self.tool_name} -n {condition} -s {opt.short_flag} -l {opt.long_flag} -x -a "{choices_str}" -d "{self.escape_string(opt.help)}"
"""
            elif opt.long_flag:
                script += f"""complete -c {self.tool_name} -n {condition} -l {opt.long_flag} -x -a "{choices_str}" -d "{self.escape_string(opt.help)}"
"""
        elif opt.is_integer_type():
            if opt.short_flag and opt.long_flag:
                script += f"""complete -c {self.tool_name} -n {condition} -s {opt.short_flag} -l {opt.long_flag} -x -a "1 2 3 4 5 6 7 8 9 10" -d "{self.escape_string(opt.help)}"
"""
            elif opt.long_flag:
                script += f"""complete -c {self.tool_name} -n {condition} -l {opt.long_flag} -x -a "1 2 3 4 5 6 7 8 9 10" -d "{self.escape_string(opt.help)}"
"""
        else:
            # Regular option
            if opt.short_flag and opt.long_flag:
                script += f"""complete -c {self.tool_name} -n {condition} -s {opt.short_flag} -l {opt.long_flag} -d "{self.escape_string(opt.help)}"
"""
            elif opt.long_flag:
                script += f"""complete -c {self.tool_name} -n {condition} -l {opt.long_flag} -d "{self.escape_string(opt.help)}"
"""

        return script

    def _generate_positional_completion(
        self, pos: PositionalInfo, condition: str
    ) -> str:
        """Generate Fish completion for a positional argument."""
        script = ""

        # Skip positionals that are actually subcommand placeholders
        if pos.dest in ["command", "mcp", "subcommand"]:
            return ""

        if pos.choices:
            choices_str = " ".join(str(c) for c in pos.choices)
            script += f"""# Positional argument: {pos.dest}
complete -c {self.tool_name} -n {condition} -x -a "{choices_str}" -d "{self.escape_string(pos.help)}"
"""
        elif pos.is_file_type():
            script += f"""# Positional argument: {pos.dest} (file)
complete -c {self.tool_name} -n {condition} -F -d "{self.escape_string(pos.help)}"
"""

        return script

    def _generate_command_groups(self) -> str:
        """Generate completions for command groups."""
        script = "\n# Command groups\n"

        # Import CommandGroup to check instances
        from pieces.base_command import CommandGroup

        for cmd in BaseCommand.commands:
            if isinstance(cmd, CommandGroup):
                # Generate subcommand completions for this group
                script += f"\n# {cmd.name} subcommands\n"

                # Show subcommands when the main command is entered
                subcommand_names = []
                subcommand_helps = {}

                for sub_name, sub_cmd in cmd.subcommands.items():
                    # Skip aliases
                    if sub_name == sub_cmd.name:
                        subcommand_names.append(sub_name)
                        subcommand_helps[sub_name] = sub_cmd.help

                # Add completion for showing subcommands
                for sub_name in sorted(subcommand_names):
                    help_text = self.escape_string(subcommand_helps[sub_name])
                    script += f'complete -c {self.tool_name} -n "__{self.tool_name}_needs_subcommand {cmd.name}" -a "{sub_name}" -d "{help_text}"\n'

                # Add completions for each subcommand's options
                for sub_name, sub_cmd in cmd.subcommands.items():
                    if sub_name != sub_cmd.name:
                        continue  # Skip aliases

                    # Get subcommand details from parser
                    sub_key = f"{cmd.name}_{sub_name}"
                    sub_details = self.parser.subcommand_details.get(sub_key, {})
                    options = sub_details.get("options", [])
                    positionals = sub_details.get("positionals", [])

                    # Generate options for this subcommand
                    condition = (
                        f'"__{self.tool_name}_using_subcommand {cmd.name} {sub_name}"'
                    )

                    for opt in options:
                        script += self._generate_option_completion(opt, condition)

                    for pos in positionals:
                        script += self._generate_positional_completion(pos, condition)

        return script

    def _generate_help_command(self) -> str:
        """Generate help command completion."""
        commands = " ".join(sorted(self.parser.commands_info.keys()))
        return f"""
# Help command - complete with available commands
complete -c {self.tool_name} -n "__{self.tool_name}_using_command help" -x -a '{commands}' -d "Get help for command"
"""


def main():
    """Main entry point for the script."""
    cli = PiecesCLI()
    parser = CommandParser(cli.parser)

    # Parse command line arguments
    if len(sys.argv) >= 2:
        shell_arg = sys.argv[1].lstrip("-")

        if shell_arg in ["bash", "zsh", "fish"]:
            try:
                generators = {
                    "bash": BashCompletionGenerator,
                    "zsh": ZshCompletionGenerator,
                    "fish": FishCompletionGenerator,
                }.get(shell_arg)

                if generators:
                    generator = generators(parser, "pieces")
                    print(generator.generate())
                else:
                    print(f"Unsupported shell: {shell_arg}", file=sys.stderr)
                    sys.exit(1)
            except Exception as e:
                print(f"Error generating {shell_arg} completion: {e}", file=sys.stderr)
                sys.exit(1)
    else:
        print("Usage: python autocomplete_generation.py [--bash|--zsh|--fish]")
        print("Generates shell completion scripts for the Pieces CLI")


if __name__ == "__main__":
    main()
