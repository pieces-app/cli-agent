from base import CompletionGenerator, CommandInfo
from pieces import __version__
from pieces.base_command import CommandGroup, BaseCommand


class BashCompletionGenerator(CompletionGenerator):
    """Generates Bash completion scripts."""

    def generate(self) -> str:
        """Generate the Bash completion script."""
        script = self._generate_header()
        script += self._generate_init_completion()
        script += self._generate_main_function()
        script += self._generate_helper_functions()
        script += self._generate_registration()
        return script.strip()

    def _generate_header(self) -> str:
        """Generate the script header."""
        return f"""#!/bin/bash
# Bash completion for {self.tool_name}
# Generated automatically - using Pieces CLI
# Version: {__version__}
"""

    def _generate_init_completion(self) -> str:
        """Generate the _init_completion function if not available."""
        return """
# Provide _init_completion if not available (e.g., on macOS without bash-completion)
if ! declare -F _init_completion >/dev/null 2>&1; then
    _init_completion() {
        local exclude flag outx errx inx OPTIND=1

        while getopts "n:e:o:i:s" flag "$@"; do
            case $flag in
                n) exclude+=$OPTARG ;;
                e) errx=$OPTARG ;;
                o) outx=$OPTARG ;;
                i) inx=$OPTARG ;;
                s) split=false ;;
            esac
        done

        # Set cur, prev, words, and cword
        cur="${COMP_WORDS[COMP_CWORD]}"
        prev="${COMP_WORDS[COMP_CWORD-1]}"
        words=("${COMP_WORDS[@]}")
        cword=$COMP_CWORD

        # Handle redirection operators
        case "$prev" in
            ">"|"<"|">>"|"&>"|"2>"|"2>&1")
                return 1
                ;;
        esac

        # Handle = in variable assignments
        if [[ $cur == *=* ]]; then
            prev=${cur%%=*}
            cur=${cur#*=}
        fi

        return 0
    }
fi

# Provide _filedir if not available
if ! declare -F _filedir >/dev/null 2>&1; then
    _filedir() {
        local IFS=$'\\n'
        
        # Simple file/directory completion
        if [[ -z "$1" ]]; then
            # Complete with files and directories
            COMPREPLY=( $(compgen -f -- "$cur") )
        else
            # Complete with specific extension
            COMPREPLY=( $(compgen -f -X '!*'"$1" -- "$cur") )
        fi
        
        # Mark directories with trailing slash
        for ((i=0; i < ${#COMPREPLY[@]}; i++)); do
            if [[ -d "${COMPREPLY[i]}" ]]; then
                COMPREPLY[i]+="/"
            fi
        done
    }
fi
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
        if [[ "$cur" == -* ]]; then
            # If current word starts with -, show options
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
        # Check if this is a command group
        is_command_group = any(
            isinstance(cmd, CommandGroup) and cmd.name == cmd_name
            for cmd in BaseCommand.commands
        )

        if is_command_group:
            # Handle command group with subcommands
            cmd_group = next(
                cmd
                for cmd in BaseCommand.commands
                if isinstance(cmd, CommandGroup) and cmd.name == cmd_name
            )

            script = f"""        {cmd_name})
            # {cmd_info.description}
            
            # Find subcommand
            local subcmd=""
            for ((i=i+1; i < cword; i++)); do
                if [[ "${{words[i]}}" != -* ]]; then
                    subcmd="${{words[i]}}"
                    break
                fi
            done
            
            if [[ -z "$subcmd" ]]; then
                # No subcommand yet, show available subcommands
                local subcommands="{" ".join(sorted(sub_name for sub_name, sub_cmd in cmd_group.subcommands.items() if sub_name == sub_cmd.name))}"
                COMPREPLY=( $(compgen -W "$subcommands" -- "$cur") )
                return 0
            fi
            
            # Handle subcommand completions
            case "$subcmd" in
"""

            # Add completions for each subcommand
            for sub_name, sub_cmd in cmd_group.subcommands.items():
                if sub_name != sub_cmd.name:  # Skip aliases
                    continue

                sub_key = f"{cmd_name}_{sub_name}"
                sub_details = self.parser.subcommand_details.get(sub_key, {})
                sub_options = sub_details.get("options", [])

                # Build options string for subcommand
                sub_option_flags = []
                for opt in sub_options:
                    sub_option_flags.extend(opt.flags)
                sub_options_str = " ".join(sub_option_flags)

                script += f"""                {sub_name})
                    local subcmd_options="{sub_options_str}"
                    
                    case "$prev" in
"""

                # Add option-specific completions for subcommand
                for opt in sub_options:
                    if opt.is_file_type():
                        for flag in opt.flags:
                            script += f"""                        {flag})
                            _filedir
                            return 0
                            ;;
"""
                    elif opt.choices:
                        choices_str = " ".join(str(c) for c in opt.choices)
                        for flag in opt.flags:
                            script += f"""                        {flag})
                            COMPREPLY=( $(compgen -W "{choices_str}" -- "$cur") )
                            return 0
                            ;;
"""

                script += """                        *)
                            COMPREPLY=( $(compgen -W "$subcmd_options" -- "$cur") )
                            return 0
                            ;;
                    esac
                    ;;
"""

            script += """                *)
                    # Unknown subcommand
                    return 0
                    ;;
            esac
            ;;
"""
            return script

        # Regular command (not a command group)
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
"""
