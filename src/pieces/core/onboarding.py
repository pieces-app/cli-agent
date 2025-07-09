from abc import ABC
from typing import Callable
import pyperclip
from rich.markdown import Markdown
from rich.panel import Panel
from rich import box
from rich.text import Text
from rich.style import Style
import os
import getpass
import platform
import sys

from pieces.core.cli_loop import run_command, extract_text
from pieces.core.config_command import ConfigCommands
from pieces.settings import Settings
from pieces.urls import URLs


def get_prompt():
    username = getpass.getuser()
    hostname = platform.node()
    path = os.getcwd()
    current_directory = os.path.basename(path)
    os_type = platform.system()

    if os_type == "Windows":
        prompt = f"{path}> "
    elif os_type == "Linux":
        prompt = f"{path}$ "
    else:
        prompt = f"{username}@{hostname} {current_directory}$ "

    return prompt


demo_snippet = f"""import requests
response = requests.get("{URLs.PIECES_APP_WEBSITE.value}")
print(response.text)
"""


class BasedOnboardingStep(ABC):
    @staticmethod
    def click_to_continue():
        Settings.logger.print("Press any key to proceed", style="dim")
        Settings.logger.input()


class OnboardingStep(BasedOnboardingStep):
    def __init__(self, text: str, validation: Callable) -> None:
        self.text = text
        self.validation = validation

    def run(self):
        Settings.logger.print(Markdown(self.text))
        self.click_to_continue()

        while True:
            validation, message_failed = self.validation()
            if validation:
                break  # Exit the loop if validation is successful
            else:
                Settings.logger.print(message_failed)
                self.click_to_continue()

        return True


class OnboardingCommandStep(BasedOnboardingStep):
    def __init__(self, text, predicted_text: str) -> None:
        self.text = text
        self.predicted_text = predicted_text

    def run(self):
        Settings.logger.print(Markdown(self.text))
        # self.click_to_continue(console)

        user_input = input(get_prompt()).strip()
        while user_input != self.predicted_text:
            if user_input == "exit":
                sys.exit(1)
            Settings.logger.print(
                Markdown(f"❌ Wrong command. Please use: `{self.predicted_text}`")
            )
            user_input = input(get_prompt()).strip()

        run_command(*extract_text(user_input.removeprefix("pieces ")))

        return True


def create_snippet_one_validation():
    text = pyperclip.paste()
    normalized_s1 = "\n".join(line.strip() for line in text.strip().splitlines())
    normalized_s2 = "\n".join(
        line.strip() for line in demo_snippet.strip().splitlines()
    )
    if normalized_s1 == normalized_s2:
        pyperclip.copy(demo_snippet)  # Copy the normalized snippet

    return (
        normalized_s1 == normalized_s2,
        "Looks like you haven't copied the material yet. Please copy the material to save it to Pieces.",
    )


def validate_login():
    message = "You can't continue if you are not signed in"
    if Settings.pieces_client.user_api.user_snapshot():
        return True, message
    return False, message


def get_shell_info():
    """Detect user's shell and return completion instructions."""
    shell_path = os.environ.get("SHELL", "")
    shell_name = os.path.basename(shell_path).lower()
    
    # Check if running in PowerShell (Windows or cross-platform)
    ps_session = os.environ.get("PSModulePath") or os.environ.get("POWERSHELL_DISTRIBUTION_CHANNEL")
    
    # Handle PowerShell detection
    if ps_session or "pwsh" in shell_name or "powershell" in shell_name:
        return {
            "name": "PowerShell",
            "config_file": "$PROFILE",
            "command": '$completionPiecesScript = pieces completion powershell | Out-String; Invoke-Expression $completionPiecesScript',
            "reload": ". $PROFILE",
        }
    # Handle common shell variations
    elif "zsh" in shell_name:
        return {
            "name": "Zsh",
            "config_file": "~/.zshrc",
            "command": 'eval "$(pieces completion zsh)"',
            "reload": "source ~/.zshrc",
        }
    elif "fish" in shell_name:
        return {
            "name": "Fish",
            "config_file": "~/.config/fish/config.fish",
            "command": "pieces completion fish | source",
            "reload": "source ~/.config/fish/config.fish",
        }
    elif "bash" in shell_name or shell_name in ["sh", ""]:
        return {
            "name": "Bash",
            "config_file": "~/.bashrc",
            "command": 'eval "$(pieces completion bash)"',
            "reload": "source ~/.bashrc",
        }
    else:
        # Default to bash for unknown shells
        return {
            "name": "Bash",
            "config_file": "~/.bashrc",
            "command": 'eval "$(pieces completion bash)"',
            "reload": "source ~/.bashrc",
        }


def get_completion_instructions():
    """Generate shell-specific completion setup instructions."""
    shell_info = get_shell_info()

    # Generate shell-specific quick setup command
    if shell_info["name"] == "PowerShell":
        quick_setup = f"""Add-Content {shell_info["config_file"]} '{shell_info["command"]}'; {shell_info["reload"]}"""
        code_block_lang = "powershell"
    else:
        quick_setup = f"""echo '{shell_info["command"]}' >> {shell_info["config_file"]} && {shell_info["reload"]}"""
        code_block_lang = "bash"

    instructions = f"""## Enable Shell Completions

Auto-complete commands and options by pressing **Tab** while typing.

**💡 Quick setup for {shell_info["name"]}:** Run this command to enable completion:
```{code_block_lang}
{quick_setup}
```

Try typing `pieces ` and press **Tab** to test it out!"""

    return instructions


def onboarding_command(**kwargs):
    step_number = 1
    steps = {
        "Step 1: Sign into Pieces": [
            OnboardingCommandStep(
                "You must be signed in to use Pieces. Type `pieces login` to sign into an account.",
                "pieces login",
            ),
            OnboardingStep("", validate_login),
        ],
        "Step 2: Save a Material": [
            OnboardingStep(
                "Let's get started by saving a material to Pieces.\n"
                "Copy the following python material: \n"
                f"```python\n{demo_snippet}\n```",
                create_snippet_one_validation,
            ),
            OnboardingCommandStep(
                "You can save the material by typing `pieces create`", "pieces create"
            ),
        ],
        "Step 3: Open your Saved materials": [
            OnboardingCommandStep(
                "Now, let's view all of your saved materials by typing `pieces list`.",
                "pieces list",
            )
        ],
        "Step 4: Start a Session": [
            OnboardingCommandStep(
                "Starting a session allows you to run multiple commands without having to start the Pieces CLI every time."
                "Start a session with `pieces run`. To exit your session, use `exit`.",
                "pieces run",
            )
        ],
        "Step 5: Chat with the Copilot": [
            OnboardingCommandStep(
                "Start a chat with the Copilot by using `pieces ask 'How to print I love Pieces CLI in Python and Java'`.",
                "pieces ask 'How to print I love Pieces CLI in Python and Java'",
            ),
            OnboardingCommandStep(
                "Create a session with Copilot by typing `pieces run` then use `ask` to interact with Copilot.",
                "pieces run",
            ),
        ],
        "Step 6: Add completion scripts": [
            OnboardingStep(
                get_completion_instructions(),
                lambda: (True, ""),
            )
        ],
        "Step 7: Sharing your Feedback": [
            OnboardingCommandStep(
                "Your feedback is very **important** to us. Please share some of your feedback by typing `pieces feedback`.",
                "pieces feedback",
            )
        ],
        "Step 8: Contributing": [
            OnboardingCommandStep(
                "The Pieces CLI is an **open source project** and you can contribute to it by creating a pull request or open an issue by typing `pieces contribute`.",
                "pieces contribute",
            )
        ],
    }

    Settings.logger.print(
        Panel(
            Text("Welcome to the Pieces CLI", justify="center", style="bold")
            + Text(
                "\nRemember Anything and Interact with Everything",
                style=Style(bold=False, dim=True),
            ),
            box=box.HEAVY,
            style="markdown.h1.border",
        )
    )

    Settings.logger.print("Whenever you want to exit the onboarding flow type `exit`.")

    if not Settings.pieces_client.open_pieces_os():
        Settings.logger.print("❌ PiecesOS is not running")
        Settings.logger.print(
            Markdown(
                "**PiecesOS** is a **required** background service"
                " that powers the Pieces CLI and all other Pieces Integrations such as:\n\n"
                "- **VS Code**\n"
                "- **JetBrains**\n"
                "- **Sublime Text**\n"
                "- **Visual Studio**\n"
                "and web browser extensions for Google Chrome and Firefox and more.\n\n"
                "for more information about the integrations check out the **documentation** https://docs.pieces.app/#ides-and-editors. \n\n"  # TODO: Add a link to the documentation extensions like the old website
                "### Key Functionalities\n"
                "- Highly contextual generative AI assistant, called **Pieces Copilot**.\n"
                "- **Materials Management** for efficient code organization enables you to save and share materials\n"
                "- **Enhanced Search Capabilities** to quickly find your materials\n"
                "- Provides the ability to process data locally, guaranteeing enhanced **privacy** and **security**."
            )
        )

        OnboardingCommandStep(
            "To install PiecesOS run `pieces install`", "pieces install"
        ).run()

    else:
        Settings.logger.print("✅ PiecesOS is running")

    Settings.startup(True)

    while step_number - 1 < len(steps):
        for step in steps:
            Settings.logger.print(step)
            for mini_step in steps[step]:
                mini_step.run()

            step_number += 1

    Settings.logger.print("Thank you for using the Pieces CLI!")
    Settings.logger.print(
        Markdown("You are now a `10x` more productive developer with Pieces.")
    )
    Settings.logger.print("For more information visit " + URLs.DOCS_CLI.value)

    config = ConfigCommands.load_config()
    config["onboarded"] = True
    ConfigCommands.save_config(config)

    from pieces._vendor.pieces_os_client.exceptions import BadRequestException

    try:
        Settings.pieces_client.connector_api.onboarded(
            Settings.pieces_client.application.id, True
        )
    except BadRequestException:
        pass
