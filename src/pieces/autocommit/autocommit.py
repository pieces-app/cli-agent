import subprocess
import re
from .git_api import get_repo_issues, get_git_repo_name
from typing import TYPE_CHECKING, Optional, Tuple
from pieces.settings import Settings
import os
from collections import defaultdict
from rich.console import Console
from rich.markdown import Markdown


if TYPE_CHECKING:
    from pieces_os_client.models.seeds import Seeds


def get_current_working_changes() -> Optional[Tuple[str, "Seeds"]]:
    """
    Fetches the detailed changes in the files you are currently working on, limited to a specific word count.

    Returns:
        Tuple of
            A string summarizing the detailed changes in a format suitable for generating commit messages.
            List of seeded asset to be input to the relevance
    """
    from pieces_os_client.models.seed import Seed
    from pieces_os_client.models.seeds import Seeds
    from pieces_os_client.models.seeded_asset import SeededAsset
    from pieces_os_client.models.seeded_asset_metadata import SeededAssetMetadata
    from pieces_os_client.models.seeded_format import SeededFormat
    from pieces_os_client.models.seeded_fragment import SeededFragment
    from pieces_os_client.models.transferable_string import TransferableString
    from pieces_os_client.models.anchor_type_enum import AnchorTypeEnum
    from pieces_os_client.models.seeded_anchor import SeededAnchor

    try:
        result = subprocess.run(
            ["git", "diff", "--staged"], capture_output=True, text=True)
        if not result.stdout.strip():
            Settings.show_error(
                "No changes found", "Please make sure you have added some files to your staging area")
            return None

        detailed_diff = result.stdout.strip()
        summary = ""
        content_file = defaultdict(str)
        lines_diff = detailed_diff.split("\n")

        for idx, line in enumerate(lines_diff):
            if line.startswith('diff --git'):
                file_changed = re.search(r'diff --git a/(.+) b/\1', line)
                if file_changed:
                    file_name = file_changed.group(1)
                    if lines_diff[idx + 1] == "new file mode 100644":
                        summary += f"File created: **{file_name}**\n"
                    elif lines_diff[idx + 1] == "deleted file mode 100644":
                        summary += f"File deleted: **{file_name}**\n"
                    else:
                        summary += f"File modified: **{file_name}**\n"
            if (line.startswith('+') and not line.startswith('+++')) or (line.startswith('-') and not line.startswith('---')):
                content_file[os.path.join(
                    os.getcwd(), *file_name.split("/"))] += line.strip()

        return summary, Seeds(
            iterable=[
                Seed(
                    asset=SeededAsset(
                        application=Settings.pieces_client.application,
                        format=SeededFormat(
                            fragment=SeededFragment(
                                string=TransferableString(raw=content)
                            )
                        ),
                        metadata=SeededAssetMetadata(
                            anchors=[
                                SeededAnchor(
                                    fullpath=file_path,
                                    type=AnchorTypeEnum.FILE
                                )
                            ]
                        )
                    ),
                    type="SEEDED_ASSET"
                )
                for file_path, content in content_file.items()
            ]
        )
    except subprocess.CalledProcessError as e:
        Settings.show_error(f"Error fetching current working changes: {e}")
        return None


def git_commit(**kwargs):
    if kwargs.get("all_flag", False):
        subprocess.run(["git", "add", "-A"], check=True)

    issue_flag = kwargs.get('issue_flag')
    try:
        changes_summary, seeds = get_current_working_changes()
    except TypeError:
        return

    commit_message = get_commit_message(changes_summary, seeds)
    if not commit_message:
        return

    if issue_flag:
        try:
            issue_number, issue_title, issue_markdown = get_issue_details(
                seeds)
        except TypeError:
            issue_flag = False

    r_message = input("The generated commit message is:"
                      f"\n\n {commit_message}\n\n"
                      "Are you sure you want to commit these changes?"
                      "\n\n- y: Yes\n- n: No\n- c: Change the commit message"
                      "\n\nPlease enter your choice (y/n/c): ").lower().strip()

    if r_message not in ["y", "c", ""]:
        print("Committing changes cancelled")
        return

    if r_message == "c":
        edit = input(
            f"Enter the new commit message [generated message is: '{commit_message}']: ")
        if edit:
            commit_message = edit

    if issue_flag:
        if issue_number:
            print("Issue Number: ", issue_number)
            print("Issue Title: ", issue_title)
            r_issue = input("Is this issue related to the commit? (y/n): ")
            if r_issue.lower() == "y":
                commit_message += f" (issue: #{issue_number})"
            else:
                issue_number = None
        if issue_number is None and issue_markdown:
            console = Console()
            md = Markdown(issue_markdown)
            console.print(md)
            validate_issue = True
            while validate_issue:
                issue_number = input(
                    "Issue number?\nLeave blank if none: ").strip()
                if issue_number.startswith("#") and issue_number[1:].isdigit():
                    issue_number = issue_number[1:]
                    validate_issue = False
                elif issue_number.isdigit():
                    validate_issue = False
                elif not issue_number:
                    break
            if not validate_issue:
                commit_message += f" (issue: #{issue_number})"

    try:
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        print("Successfully committed with message:", commit_message)
        if kwargs.get('push', False):
            subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        print("Failed to commit changes:", e)


def get_issue_details(seeds):
    from pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
    from pieces_os_client.models.qgpt_relevance_input_options import QGPTRelevanceInputOptions

    issue_prompt = """Please provide the issue number that is related to the changes, If nothing related write 'None'.
            `Output format WITHOUT ADDING ANYTHING ELSE: "Issue: **ISSUE NUMBER OR NONE HERE**`,
            `Example: 'Issue: 12', 'Issue: None'`,
            `Note: Don't provide any other information`
            `Here are the issues:`\n{issues}"""

    # Issues
    repo_details = get_git_repo_name()
    # Check if we got a vaild repo name
    issues = get_repo_issues(*repo_details) if repo_details else []

    if issues:
        try:
            # Make the issues look nicer
            issue_markdown = [
                (f"- `Issue_number: {issue['number']}`\n"
                    f"`Title: {issue['title']}`\n"
                 f"- `Body: {issue['body']}`")
                for issue in issues
            ]
            issue_markdown = "\n".join(issue_markdown)  # To string
            issue_number = Settings.pieces_client.qgpt_api.relevance(
                QGPTRelevanceInput(
                    query=issue_prompt.format(issues=issue_markdown),
                    application=Settings.pieces_client.application.id,
                    model=Settings.pieces_client.model_name,
                    options=QGPTRelevanceInputOptions(question=True),
                    seeds=seeds
                )).answer.answers.iterable[0].text

            # Extract the issue part
            issue_number = issue_number.replace("Issue: ", "")
            # If the issue is a number
            issue_number = int(issue_number)
            issue_title = next(
                (issue["title"] for issue in issues if issue["number"] == issue_number), None)
        except:
            issue_number = None
            issue_title = ""
            issue_markdown = ""
        return issue_number, issue_title, issue_markdown


def get_commit_message(changes_summary, seeds):
    from pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
    from pieces_os_client.models.qgpt_relevance_input_options import QGPTRelevanceInputOptions

    message_prompt = f"""Act as a git expert developer to generate a concise git commit message **using best git commit message practices** to follow these specifications:
                `Message language: English`,
                `Format of the message: "(task done): small description"`,
                `task done can be one from: "feat,fix,chore,refactor,docs,style,test,perf,ci,build,revert"`,
                `Example of the message: "docs: add new guide on python"`,
                Your response should be: `__The message is: **YOUR COMMIT MESSAGE HERE**__` WITHOUT ADDING ANYTHING ELSE",
                `Here are the changes summary:`\n{changes_summary}`
                The actual code changes provide to you in the seeds,
                `The changed parts is provided in the context where if the line start with "+"  means that line is added or "-" if it is removed"""

    try:
        commit_message = Settings.pieces_client.qgpt_api.relevance(
            QGPTRelevanceInput(
                query=message_prompt,
                seeds=seeds,
                application=Settings.pieces_client.application.id,
                model=Settings.get_model_id(),
                options=QGPTRelevanceInputOptions(question=True)
            )).answer.answers.iterable[0].text

        # Remove extras from the commit message
        # Remove the "message is" part as mentioned in the prompt
        commit_message = commit_message.replace("The message is:", "", 1)
        # Remove the bold and italic characters
        commit_message = commit_message.replace('*', '')
        # Remove the bold and italic characters
        commit_message = commit_message.replace('__', '')
        # Remove leading and trailing whitespace
        commit_message = commit_message.strip()
    except Exception as e:
        Settings.show_error("Error in getting the commit message", e)
        return
    return commit_message
