from base import CompletionGenerator, CommandInfo, OptionInfo
from pieces import __version__


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
# Generated automatically - using Pieces CLI
# Version: {__version__}
"""

    def _generate_main_function(self) -> str:
        """Generate the main completion function."""
        script = f"""
_{self.tool_name}() {{
    local line state

    _arguments -C \\
        "1: :->cmds" \\
        "*::arg:->args" \\
        '--help -h[Show help message]' \\
        '--version -v[Show version]' \\
        '--ignore-onboarding[Ignore onboarding for this command]'

    case "$state" in
        cmds)
            _values "commands" \\
"""

        # Add commands with descriptions
        for cmd_name, cmd_info in sorted(self.parser.commands_info.items()):
            description = self.escape_string(cmd_info.help)
            script += f"""                "{cmd_name}[{description}]" \\
"""

        # Add aliases
        for alias, main_cmd in sorted(self.parser.aliases_map.items()):
            description = self.escape_string(self.parser.commands_info[main_cmd].help)
            script += f"""                "{alias}[Alias for {main_cmd}: {description}]" \\
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
        # Check if this is a command group
        from pieces.base_command import CommandGroup, BaseCommand

        is_command_group = any(
            isinstance(cmd, CommandGroup) and cmd.name == cmd_name
            for cmd in BaseCommand.commands
        )

        if is_command_group:
            return self._generate_command_group_function(cmd_name, cmd_info)

        cmd_details = self.parser.subcommand_details.get(cmd_name, {})
        options = cmd_details.get("options", [])
        positionals = cmd_details.get("positionals", [])

        script = f"""
_{self.tool_name}_{cmd_name}() {{
    # Completion for '{cmd_name}' command
    _arguments \\
"""

        # Add positional arguments
        for i, pos in enumerate(positionals, 1):
            if pos.choices:
                choices = " ".join(str(c) for c in pos.choices)
                script += f"""        '{i}::{pos.dest}:({choices})' \\
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

    def _generate_command_group_function(
        self, cmd_name: str, cmd_info: CommandInfo
    ) -> str:
        """Generate completion function for a command group."""
        from pieces.base_command import CommandGroup, BaseCommand

        # Find the command group instance
        cmd_group = None
        for cmd in BaseCommand.commands:
            if isinstance(cmd, CommandGroup) and cmd.name == cmd_name:
                cmd_group = cmd
                break

        if not cmd_group:
            return ""

        script = f"""
_{self.tool_name}_{cmd_name}() {{
    local line state
    
    _arguments -C \\
        "1: :->subcmds" \\
        "*::arg:->args"
    
    case "$state" in
        subcmds)
            _values "subcommands" \\
"""

        # Add subcommands
        for sub_name, sub_cmd in sorted(cmd_group.subcommands.items()):
            if sub_name == sub_cmd.name:  # Skip aliases
                description = self.escape_string(sub_cmd.help)
                script += f"""                "{sub_name}[{description}]" \\
"""

        script = script.rstrip(" \\\n")
        script += """
            ;;
        args)
            case $line[1] in
"""

        # Add subcommand-specific completions
        for sub_name, sub_cmd in cmd_group.subcommands.items():
            if sub_name == sub_cmd.name:  # Skip aliases
                script += f"""                {sub_name})
                    _{self.tool_name}_{cmd_name}_{sub_name}
                    ;;
"""

        script += """            esac
            ;;
    esac
}
"""

        # Generate functions for each subcommand
        for sub_name, sub_cmd in cmd_group.subcommands.items():
            if sub_name == sub_cmd.name:  # Skip aliases
                script += self._generate_subcommand_function(
                    cmd_name, sub_name, sub_cmd
                )

        return script

    def _generate_subcommand_function(
        self, parent_cmd: str, sub_name: str, sub_cmd
    ) -> str:
        """Generate completion function for a subcommand."""
        sub_key = f"{parent_cmd}_{sub_name}"
        sub_details = self.parser.subcommand_details.get(sub_key, {})
        options = sub_details.get("options", [])
        positionals = sub_details.get("positionals", [])

        script = f"""
_{self.tool_name}_{parent_cmd}_{sub_name}() {{
    # Completion for '{parent_cmd} {sub_name}' subcommand
    _arguments \\
"""

        # Add positional arguments
        for i, pos in enumerate(positionals, 1):
            if pos.choices:
                choices = " ".join(str(c) for c in pos.choices)
                script += f"""        '{i}::{pos.dest}:({choices})' \\
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

        help_text = self.escape_string(opt.help)

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

    def escape_string(self, text: str) -> str:
        """Escape special characters for Zsh."""
        # In Zsh completion descriptions, we need to escape single quotes properly
        # The format is: "command[description]" where description can contain quotes
        text = text.replace("'", "'\\''")
        # Replace newlines with spaces
        text = text.replace("\n", " ")
        return text

