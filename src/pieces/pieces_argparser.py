import argparse
import sys
from rich.console import Console
from pieces.urls import URLs


class PiecesArgparser(argparse.ArgumentParser):
    parser: "PiecesArgparser"

    def __init__(self, *args, **kwargs):
        self.console = Console()
        self.err_console = Console(stderr=True)
        self.command = kwargs.pop("command_object", None)
        super().__init__(*args, **kwargs)

    def error(self, message):
        if "invalid choice" in message:
            try:
                invalid_command = message.split("'")[1]
                similar_command = self.find_most_similar_command(
                    list(self._subparsers._group_actions[0].choices.keys()),
                    invalid_command,
                )

                self.err_console.print(
                    f"[bold red]Invalid command:[/] [yellow]'{invalid_command}'[/]\n"
                    + f"Did you mean [green][bold]{similar_command}[/bold][/]?"
                    if similar_command
                    else "",
                )
            except (IndexError, AttributeError):
                self.err_console.print(
                    "[bold red]Invalid command[/]",
                )
                self.err_console.print(message)
        else:
            self.err_console.print(
                f"[bold red]{message}[/]",
            )
        sys.exit(2)

    def format_usage(self):
        """Override the standard usage formatter to use Rich styling with bracket syntax."""
        # Get the raw usage text from the parent's format_usage method
        raw_usage = super().format_usage()

        # Format the usage text with Rich styling using bracket syntax
        usage_parts = raw_usage.split("usage: ", 1)
        if len(usage_parts) > 1:
            program_name, arguments = usage_parts[1].split(" ", 1)

            # Create styled text using bracket syntax
            styled_usage = "[bold yellow]usage:[/] [green]" + program_name + "[/] "

            # Format different argument types
            current_text = ""
            in_optional = False
            in_required = False

            for char in arguments:
                if char == "[":
                    if current_text:
                        styled_usage += current_text
                        current_text = ""
                    styled_usage += "[cyan]["
                    in_optional = True
                elif char == "]":
                    styled_usage += "][/cyan]"
                    in_optional = False
                    current_text = ""
                elif char == "{":
                    if current_text:
                        styled_usage += current_text
                        current_text = ""
                    styled_usage += "[magenta]{"
                    in_required = True
                elif char == "}":
                    styled_usage += "}[/magenta]"
                    in_required = False
                    current_text = ""
                else:
                    if in_optional or in_required:
                        styled_usage += char
                    else:
                        current_text += char

            if current_text:
                styled_usage += current_text

            return styled_usage

        return raw_usage

    def print_help(self, file=None):
        console = self.console

        # HEADER
        default_desc = f"Pieces CLI {self.prog.split(' ')[-1].title()} Command"
        console.print(f"[bold blue]{self.description or default_desc}[/]")

        console.print(self.format_usage(), "\n")

        # Collect all actions by type
        pos_actions = [
            action
            for action in self._actions
            if action.option_strings == [] and action.dest != "help"
        ]

        opt_actions = [
            action
            for action in self._actions
            if action.option_strings != [] or action.dest == "help"
        ]

        # Find the maximum width for alignment
        max_width = 4  # Minimum width
        for action in pos_actions:
            max_width = max(max_width, len(action.dest) + 4)  # +2 for the indentation

        for action in opt_actions:
            flags = ", ".join(action.option_strings)
            max_width = max(max_width, len(flags) + 4)  # +2 for the indentation

        if not self.prog == "pieces":
            pos_text = "[bold cyan]Positional Arguments:[/]\n"
            if pos_actions:
                for action in pos_actions:
                    arg_name = f"  {action.dest}"
                    padding = " " * (max_width - len(arg_name))
                    if action.choices:
                        pos_text += f"[green bold]{arg_name}[/]{padding}- {', '.join(action.choices)}\n"
                    elif action.help:
                        pos_text += (
                            f"[green bold]{arg_name}[/]{padding}- {action.help}\n"
                        )
            if len(pos_text.splitlines()) > 1:
                console.print(pos_text)

        if opt_actions:
            console.print("[bold cyan]Optional Arguments:[/]")
            for action in opt_actions:
                flags = f"  {', '.join(action.option_strings)}"
                padding = " " * (max_width - len(flags))
                console.print(
                    f"[green bold]{flags}[/]{padding}- {action.help or 'No description available'}"
                )
            console.print()

        # Format subcommands if any
        if hasattr(self, "_subparsers") and self._subparsers:
            for action in self._actions:
                if isinstance(action, argparse._SubParsersAction):
                    console.print("[bold cyan]Available Commands:[/]")

                    # Calculate maximum command width for proper alignment
                    cmd_max_width = 4
                    for choice in action.choices.keys():
                        cmd_max_width = max(
                            cmd_max_width, len(choice) + 4
                        )  # +2 for indentation

                    # Print aligned commands
                    for choice in action.choices.keys():
                        cmd_name = f"  {choice}"
                        padding = " " * (cmd_max_width - len(cmd_name))
                        help_text = None
                        for subaction in action._choices_actions:
                            if subaction.dest == choice:
                                help_text = subaction.help
                                break
                        if not help_text:
                            continue
                        console.print(
                            f"[green bold]{cmd_name}[/]{padding}- {help_text}"
                        )

        if self.command and hasattr(self.command, "examples") and self.command.examples:
            console.print("\n[bold cyan]Examples:[/]")
            for example in self.command.examples:
                console.print(f"  [yellow]{example}[/]")

        if self.prog == "pieces":
            docs = URLs.DOCS_CLI.value
        else:
            docs = self.command.docs if self.command else None
        if docs:
            console.print("\n[bold cyan]Documentation:[/]")
            console.print(f"  [blue underline]{docs}[/]")

        if self.prog == "pieces":
            console.print(
                "\n[dim]For detailed help on specific commands, use: [bold]pieces command --help[/][/]"
            )
        else:
            console.print("\n[dim]For more help, use: [bold]pieces --help[/][/]")

    @classmethod
    def levenshtein_distance(cls, s1, s2):
        # If s1 is shorter than s2, swap them to minimize the number of operations
        if len(s1) < len(s2):
            return cls.levenshtein_distance(s2, s1)

        # If one of the strings is empty, the distance is the length of the other string
        if len(s2) == 0:
            return len(s1)

        # Initialize the previous row of distances
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            # Initialize the current row, starting with the deletion distance
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Calculate the cost of insertions, deletions, and substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                # Append the minimum cost of the operations to the current row
                current_row.append(min(insertions, deletions, substitutions))
            # Set the current row as the previous row for the next iteration
            previous_row = current_row

        # The last element of the previous row contains the levenshtein distance
        return previous_row[-1]

    @classmethod
    def find_most_similar_command(cls, valid_commands, user_input):
        # Calculate the Levenshtein distance between the user input and each valid command
        distances = {
            cmd: cls.levenshtein_distance(user_input, cmd) for cmd in valid_commands
        }
        # Find the command with the smallest Levenshtein distance to the user input
        most_similar_command = min(distances, key=distances.get)
        return most_similar_command
