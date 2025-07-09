from base import CompletionGenerator, CommandInfo
from pieces import __version__
from pieces.base_command import CommandGroup, BaseCommand


class PowerShellCompletionGenerator(CompletionGenerator):
    """Generates PowerShell completion scripts."""

    def generate(self) -> str:
        """Generate the PowerShell completion script."""
        script = self._generate_header()
        script += self._generate_main_function()
        script += self._generate_registration()
        return script.strip()

    def _generate_header(self) -> str:
        """Generate the script header."""
        return f"""using namespace System.Management.Automation
using namespace System.Management.Automation.Language

# PowerShell completion for {self.tool_name}
# Generated automatically - using Pieces CLI
# Version: {__version__}

"""

    def _generate_main_function(self) -> str:
        """Generate the main completion function."""
        all_commands = sorted(
            set(
                list(self.parser.commands_info.keys())
                + list(self.parser.aliases_map.keys())
            )
        )

        # Build dynamic parameter choices
        param_choices = self._build_parameter_choices()

        script = f"""Register-ArgumentCompleter -Native -CommandName '{self.tool_name}' -ScriptBlock {{
    param($wordToComplete, $commandAst, $cursorPosition)
    
    # Initialize variables
    $commandElements = $commandAst.CommandElements
    $commandPath = @()
    $lastParameter = $null
    $expectingParameterValue = $false
    
    # Parse command line dynamically
    for ($i = 0; $i -lt $commandElements.Count; $i++) {{
        $element = $commandElements[$i]
        
        # Skip if not a string constant
        if ($element -isnot [StringConstantExpressionAst]) {{
            continue
        }}
        
        $elementValue = $element.Value
        $isLastElement = ($i -eq ($commandElements.Count - 1))
        
        # First element should be the command name
        if ($i -eq 0) {{
            if ($elementValue -ne '{self.tool_name}') {{
                return @()  # Not our command
            }}
            $commandPath += $elementValue
            continue
        }}
        
        # Check if this is a parameter (starts with -)
        if ($elementValue.StartsWith('-')) {{
            $lastParameter = $elementValue
            $expectingParameterValue = $true
            
            # If this is the last element and we're still typing it
            if ($isLastElement -and $cursorPosition -le $element.Extent.EndOffset) {{
                $expectingParameterValue = $false
            }}
        }}
        else {{
            # This is a value (command, subcommand, or parameter value)
            if ($expectingParameterValue) {{
                # It's a parameter value, reset the flag
                $expectingParameterValue = $false
                $lastParameter = $null
            }}
            else {{
                # It's a command or subcommand
                # Only add to path if we're not currently typing it
                if (-not $isLastElement -or $cursorPosition -gt $element.Extent.EndOffset) {{
                    $commandPath += $elementValue
                }}
            }}
        }}
    }}
    
    # Determine what we're completing
    $completingParameterValue = $false
    if ($expectingParameterValue -and $lastParameter) {{
        $completingParameterValue = $true
    }}
    
    # Build the command path string for lookup
    $pathKey = $commandPath -join ';'
    
    # Define parameter value choices
    $parameterValueChoices = @{{
"""

        # Add parameter choices
        for path, param, choices in param_choices:
            choices_str = ', '.join(f"'{c}'" for c in choices)
            script += f"        '{path};{param}' = @({choices_str})\n"

        script += """    }
    
    # Get completions
    $completions = @()
    
    if ($completingParameterValue) {
        # Complete parameter value
        $lookupKey = "$pathKey;$lastParameter"
        if ($parameterValueChoices.ContainsKey($lookupKey)) {
            foreach ($choice in $parameterValueChoices[$lookupKey]) {
                $completions += [CompletionResult]::new($choice, $choice, 'ParameterValue', $choice)
            }
        }
    }
    else {
        # Complete commands, subcommands, or parameters
        switch ($pathKey) {
"""

        # Generate root completions
        script += f"""            '{self.tool_name}' {{
                # Root level - show commands
"""
        for cmd_name in all_commands:
            cmd_info = self.parser.commands_info.get(cmd_name)
            if cmd_info:
                description = self.escape_string(cmd_info.help)
                script += f"""                $completions += [CompletionResult]::new('{cmd_name}', '{cmd_name}', 'Command', '{description}')
"""

        script += """                # Global options
                $completions += [CompletionResult]::new('--help', '--help', 'ParameterName', 'Show help message')
                $completions += [CompletionResult]::new('-h', '-h', 'ParameterName', 'Show help message')
                $completions += [CompletionResult]::new('--version', '--version', 'ParameterName', 'Show version')
                $completions += [CompletionResult]::new('-v', '-v', 'ParameterName', 'Show version')
                $completions += [CompletionResult]::new('--ignore-onboarding', '--ignore-onboarding', 'ParameterName', 'Skip onboarding')
            }
"""

        # Generate command-specific completions
        for cmd_name, cmd_info in self.parser.commands_info.items():
            script += self._generate_command_completion(cmd_name, cmd_info)

        # Generate alias completions
        for alias, main_cmd in self.parser.aliases_map.items():
            main_cmd_info = self.parser.commands_info.get(main_cmd)
            if main_cmd_info:
                script += self._generate_command_completion(alias, main_cmd_info, is_alias=True)

        script += """            default {
                # Unknown path
            }
        }
    }
    
    # Filter completions
    $filtered = @()
    foreach ($completion in $completions) {
        if ([string]::IsNullOrEmpty($wordToComplete) -or $completion.CompletionText.StartsWith($wordToComplete, [StringComparison]::OrdinalIgnoreCase)) {
            $filtered += $completion
        }
    }
    
    # Return filtered completions
    # If empty, return empty array (prevents file completion)
    return $filtered
}
"""
        return script

    def _build_parameter_choices(self):
        """Build parameter choices dynamically."""
        choices = []
        
        # Process regular commands
        for cmd_name, cmd_info in self.parser.commands_info.items():
            cmd_details = self.parser.subcommand_details.get(cmd_name, {})
            options = cmd_details.get("options", [])
            
            for opt in options:
                if opt.choices:
                    for flag in opt.flags:
                        path = f"{self.tool_name};{cmd_name}"
                        choices.append((path, flag, opt.choices))
            
            # Handle command groups
            if self._is_command_group(cmd_name):
                cmd_group = next(
                    cmd for cmd in BaseCommand.commands
                    if isinstance(cmd, CommandGroup) and cmd.name == cmd_name
                )
                
                for sub_name, sub_cmd in cmd_group.subcommands.items():
                    if sub_name != sub_cmd.name:
                        continue
                    
                    sub_key = f"{cmd_name}_{sub_name}"
                    sub_details = self.parser.subcommand_details.get(sub_key, {})
                    sub_options = sub_details.get("options", [])
                    
                    for opt in sub_options:
                        if opt.choices:
                            for flag in opt.flags:
                                path = f"{self.tool_name};{cmd_name};{sub_name}"
                                choices.append((path, flag, opt.choices))
        
        return choices

    def _generate_command_completion(self, cmd_name: str, cmd_info: CommandInfo, is_alias: bool = False) -> str:
        """Generate completion for a specific command."""
        is_command_group = self._is_command_group(cmd_name)

        if is_command_group:
            cmd_group = next(
                cmd for cmd in BaseCommand.commands
                if isinstance(cmd, CommandGroup) and cmd.name == cmd_name
            )

            script = f"""            '{self.tool_name};{cmd_name}' {{
                # {cmd_info.description}
"""
            # Add subcommands
            for sub_name, sub_cmd in cmd_group.subcommands.items():
                if sub_name != sub_cmd.name:
                    continue
                sub_description = self.escape_string(sub_cmd.help)
                script += f"""                $completions += [CompletionResult]::new('{sub_name}', '{sub_name}', 'Command', '{sub_description}')
"""
            script += """            }
"""

            # Generate subcommand completions
            for sub_name, sub_cmd in cmd_group.subcommands.items():
                if sub_name != sub_cmd.name:
                    continue

                sub_key = f"{cmd_name}_{sub_name}"
                sub_details = self.parser.subcommand_details.get(sub_key, {})
                sub_options = sub_details.get("options", [])

                script += f"""            '{self.tool_name};{cmd_name};{sub_name}' {{
                # {sub_cmd.help}
"""
                for opt in sub_options:
                    help_text = self.escape_string(opt.help)
                    for flag in opt.flags:
                        script += f"""                $completions += [CompletionResult]::new('{flag}', '{flag}', 'ParameterName', '{help_text}')
"""
                script += """            }
"""
            return script

        # Regular command
        cmd_details = self.parser.subcommand_details.get(cmd_name, {})
        options = cmd_details.get("options", [])
        positionals = cmd_details.get("positionals", [])

        script = f"""            '{self.tool_name};{cmd_name}' {{
                # {cmd_info.description}
"""
        
        # Add options
        for opt in options:
            help_text = self.escape_string(opt.help)
            for flag in opt.flags:
                script += f"""                $completions += [CompletionResult]::new('{flag}', '{flag}', 'ParameterName', '{help_text}')
"""
        
        # Add positional arguments with choices
        for pos in positionals:
            if pos.choices:
                for choice in pos.choices:
                    script += f"""                $completions += [CompletionResult]::new('{choice}', '{choice}', 'ParameterValue', 'Valid choice for {pos.dest}')
"""
        
        script += """            }
"""
        return script

    def _is_command_group(self, cmd_name: str) -> bool:
        """Check if a command is a command group."""
        return any(
            isinstance(cmd, CommandGroup) and cmd.name == cmd_name
            for cmd in BaseCommand.commands
        )

    def _generate_registration(self) -> str:
        return ""

    def escape_string(self, text: str) -> str:
        """Escape special characters for PowerShell."""
        if not text:
            return ""
        escaped = text.replace("'", "''").replace("\n", " ").replace("\r", "")
        if len(escaped) > 80:
            escaped = escaped[:77] + "..."
        return escaped
