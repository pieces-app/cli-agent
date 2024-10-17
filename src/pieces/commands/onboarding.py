from abc import ABC
from typing import Callable
import pyperclip
from rich.markdown import Markdown
from rich.console import Console
import os
import getpass
import platform
import sys

from pieces.commands.cli_loop import run_command, extract_text
from pieces.settings import Settings

def get_prompt():
    username = getpass.getuser()
    hostname = platform.node()
    path = os.getcwd()
    current_directory = os.path.basename(path)
    os_type = platform.system()

    if os_type == "Windows":
        prompt = f"{path}"
    elif os_type == "Linux":
        prompt = f"{path}$ "
    else:
        prompt = f"{username}@{hostname} {current_directory}$ "
    
    return prompt

def main():
    while True:
        # Display the prompt
        prompt = get_prompt()
        command = input(prompt)
        
        # Exit the loop if the user types 'exit'
        if command.lower() == 'exit':
            break
        
        # Execute the command (for demonstration purposes, we'll just print it)
        print(f"Executing: {command}")

if __name__ == "__main__":
    main()


demo_snippet = """import requests
response = requests.get("https://docs.pieces.app")
print(response.text)
"""

class BasedOnboardingStep(ABC):
    @staticmethod
    def click_to_continue(console:Console):
        console.print("Press any key to proceed", style="dim")
        input()

class OnboardingStep(BasedOnboardingStep):
    def __init__(self,text:str, validation: Callable) -> None:
        self.text = text
        self.validation = validation
    def run(self, console:Console):
        console.print(Markdown(self.text))
        self.click_to_continue(console)
        
        while True:
            validation, message_failed = self.validation()
            if validation:
                break  # Exit the loop if validation is successful
            else:
                console.print(message_failed)
                self.click_to_continue(console)
        
        return True

class OnboardingCommandStep(BasedOnboardingStep):
    def __init__(self,text, predicted_text: str) -> None:
        self.text = text
        self.predicted_text = predicted_text
    def run(self, console:Console):
        console.print(Markdown(self.text))
        # self.click_to_continue(console)
        
        user_input = input(get_prompt()).strip()
        while user_input != self.predicted_text:
            if user_input == "exit":
                sys.exit(1)
            console.print(Markdown(f"❌ Wrong command entered, You should type: `{self.predicted_text}`"))
            user_input = input(get_prompt()).strip()

        run_command(*extract_text(user_input.removeprefix("pieces ")))

        return True

def create_snippet_one_validation():
    text = pyperclip.paste()
    normalized_s1 = '\n'.join(line.strip() for line in text.strip().splitlines())
    normalized_s2 = '\n'.join(line.strip() for line in demo_snippet.strip().splitlines())

    return normalized_s1 == normalized_s2 , "Seems you did not copy the snippet yet"

def onboarding_command(**kwargs):
    console = Console()
    step_number = 1
    steps = {
        "Step 1: Creating a snippet":[
            OnboardingStep("Let's get started by saving a snippet\n"
                    "copy the following snippet python snippet: \n"
                    f"```python\n{demo_snippet}\n```",
                    create_snippet_one_validation
                ),
            OnboardingCommandStep(
                "You can save a snippet by typing `pieces create`",
                "pieces create"
            )
        ],
        "Step 2: Opening the created snippet":[
            OnboardingCommandStep(
                "Now let's checkout all the saved snippets by typing `pieces list`",
                "pieces list"
            )
        ],
        "Step 3: Run in loop":[
            OnboardingStep(
                "Running in loop help you to create a session with the Copilot which we will be convering " 
                "or perform an opration on the same snippet multiple times which will increase your **productivity**",
                lambda: (True, "")
            ),
            OnboardingCommandStep(
                "You can run in loop by typing `pieces run` Don't forget to exit the loop by typing `exit`",
                "pieces run"
            )
        ],
        "Step 5: Chat with the Copilot":[
            OnboardingCommandStep(
                "Now you understood what is `pieces run` let's try to interact with the Copilot by typing `pieces ask 'How to print I love Pieces CLI in Python and Java'`",
                "pieces ask 'How to print I love Pieces CLI in Python and Java'"
            ),
            OnboardingCommandStep(
                "Well you just asked one question in a conversation, " "Let's create a session with Copilot by typing `pieces run` then use `ask` to interact with Copilot",
                "pieces run"
            ),
            
        ],
        "Step 6: Sharing your feedback" : [
            OnboardingCommandStep(
                "Your feedback is very **important** for us to improve feel free to share your feedback by typing `pieces feedback`",
                "pieces feedback"
            )
        ],
        "Step 7: Contributing":[
            OnboardingCommandStep(
                "Pieces is a **open source project** and you can contribute to it by creating a pull request or open an issue by typing `pieces contribute`",
                "pieces contribute"
            )
        ]
    }
    console.print("Welcome to Pieces CLI")
    console.print("Whenever you want to exit the onboarding flow type `exit`")
    console.print("Remeber anything and Everything")
    if not Settings.pieces_client.open_pieces_os():
        console.print("❌ Pieces OS is not running")
        console.print(
            Markdown(
                "# Pieces OS\n\n"
                "**Pieces OS** is a background service" 
                " powering Pieces CLI and operating all Pieces services such as IDE integrations:\n\n"
                "- **VS Code**\n"
                "- **Jetbrains IDEs**\n"
                "- **Sublime Text**\n"
                "- **Visual Studio**\n"
                "and other web browser integrations like **Google Chrome** and **Firefox** and more.\n\n"
                "Where you have the choice to process locally, ensuring **privacy** and **security**.\n\n"
                "for more information about the ingrations check out the **documentation** https://docs.pieces.app. \n\n"

                "### Key Functionalities\n"

                "- **AI Assistant** and Copilot\n"
                "- **Snippet Management** for efficient code organization enables you to save and share snippets\n"
                "- **Enhanced Search Capabilities** to quickly find your snippets"
            )
        )

        OnboardingCommandStep(
            "To install Pieces OS run `pieces install`",
            "pieces install"
        ).run(console)

    else:
        console.print("✅ Pieces OS is running")
    
    Settings.startup()
    

    while step_number - 1 < len(steps):
        for step in steps:
            console.print(step)
            for mini_step in steps[step]:
                mini_step.run(console)

            step_number += 1
    
    console.print("Thank you for using Pieces CLI!")
    console.print("You are now 10x more productive developer with Pieces")
    console.print("For more information visit https://docs.pieces.app/extensions-plugins/cli")


