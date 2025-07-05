import subprocess
import re
import os
from collections import defaultdict
from typing import TYPE_CHECKING, Optional, Tuple
from rich.markdown import Markdown
from .git_api import get_repo_issues, get_git_repo_name
from pieces.settings import Settings

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.seeds import Seeds


def get_current_working_changes() -> Optional[Tuple[str, "Seeds"]]:
    """
    Fetches the detailed changes in the files you are currently working on, limited to a specific word count.

    Returns:
        Tuple of
            A string summarizing the detailed changes in a format suitable for generating commit messages.
            List of seeded asset to be input to the relevance
    """
    from pieces._vendor.pieces_os_client.models.seed import Seed
    from pieces._vendor.pieces_os_client.models.seeds import Seeds
    from pieces._vendor.pieces_os_client.models.seeded_asset import SeededAsset
    from pieces._vendor.pieces_os_client.models.seeded_asset_metadata import SeededAssetMetadata
    from pieces._vendor.pieces_os_client.models.seeded_format import SeededFormat
    from pieces._vendor.pieces_os_client.models.seeded_fragment import SeededFragment
    from pieces._vendor.pieces_os_client.models.transferable_string import TransferableString
    from pieces._vendor.pieces_os_client.models.anchor_type_enum import AnchorTypeEnum
    from pieces._vendor.pieces_os_client.models.seeded_anchor import SeededAnchor

    try:
        result = subprocess.run(
            ["git", "diff", "--staged"], capture_output=True, text=True, check=True
        )
        if not result.stdout.strip():
            Settings.show_error(
                "No changes found",
                "Please make sure you have added some files to your staging area",
            )
            return None

        detailed_diff = result.stdout.strip()
        summary, content_file = parse_git_diff(detailed_diff)

        seeds = Seeds(
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
                                    fullpath=file_path, type=AnchorTypeEnum.FILE
                                )
                            ]
                        ),
                    ),
                    type="SEEDED_ASSET",
                )
                for file_path, content in content_file.items()
            ]
        )
        return summary, seeds

    except subprocess.CalledProcessError as e:
        Settings.show_error(f"Error fetching current working changes: {e}")
        return None


def parse_git_diff(detailed_diff: str) -> Tuple[str, defaultdict]:
    """
    Parses the detailed git diff output to extract a summary of changes and the content of changed files.

    Args:
        detailed_diff (str): The output from a git diff command.

    Returns:
        Tuple[str, defaultdict]: A summary of changes and a dictionary mapping file paths to their changed content.
    """
    summary = []
    content_file = defaultdict(str)
    lines_diff = detailed_diff.split("\n")
    current_file = None

    for idx, line in enumerate(lines_diff):
        if line.startswith("diff --git"):
            file_changed = re.search(r"diff --git a/(.+) b/\1", line)
            if file_changed:
                current_file = file_changed.group(1)
                summary.append(get_file_change_summary(lines_diff, idx, current_file))
        elif current_file and (
            (line.startswith("+") and not line.startswith("+++"))
            or (line.startswith("-") and not line.startswith("---"))
        ):
            if line.strip() == "-" or line.strip() == "+":
                continue
            content_file[os.path.join(os.getcwd(), *current_file.split("/"))] += (
                line.strip() + "\n"
            )

    return "\n".join(summary), content_file


def get_file_change_summary(lines_diff: list, idx: int, file_name: str) -> str:
    """
    Generates a summary of changes for a specific file based on the git diff output.

    Args:
        lines_diff (list): List of lines from the git diff output.
        idx (int): Current index in the lines_diff list.
        file_name (str): Name of the file being processed.

    Returns:
        str: A summary of the changes for the file.
    """
    if idx + 1 < len(lines_diff):
        if lines_diff[idx + 1] == "new file mode 100644":
            return f"File created: **{file_name}**"
        elif lines_diff[idx + 1] == "deleted file mode 100644":
            return f"File deleted: **{file_name}**"
    return f"File modified: **{file_name}**"


def git_commit(**kwargs):
    if kwargs.get("all_flag", False):
        subprocess.run(["git", "add", "-A"], check=True)

    issue_flag = kwargs.get("issue_flag", False)
    changes = get_current_working_changes()

    if changes is None:
        Settings.show_error("No changes found or error fetching changes.")
        return

    changes_summary, seeds = changes

    commit_message = get_commit_message(changes_summary, seeds)
    if not commit_message:
        return

    issue_number = None
    issue_title = None
    issue_markdown = None
    if issue_flag:
        ans = get_issue_details(seeds)
        if ans:
            issue_number, issue_title, issue_markdown = ans

    commit_message = prompt_commit_message(
        commit_message, issue_flag, issue_number, issue_title, issue_markdown
    )
    if not commit_message:
        return

    try:
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        Settings.logger.print("Successfully committed with message:", commit_message)
        if kwargs.get("push", False):
            subprocess.run(["git", "push"], check=True)
    except subprocess.CalledProcessError as e:
        Settings.logger.print("Failed to commit changes:", e)


def prompt_commit_message(
    commit_message: str,
    issue_flag: bool,
    issue_number: Optional[int],
    issue_title: str,
    issue_markdown: str,
) -> Optional[str]:
    r_message = Settings.logger.prompt(
        "The generated commit message is:"
        f"\n\n {commit_message}\n\n"
        "Are you sure you want to commit these changes?"
        "\n\n- y: Yes\n- n: No\n- c: Change the commit message",
        choices=["y", "n", "c"],
    )

    if r_message == "c":
        edit = Settings.logger.prompt(
            f"Enter the new commit message [generated message is: '{commit_message}']"
        )
        if edit:
            commit_message = edit
    if r_message == "n":
        return

    if issue_flag and issue_number:
        Settings.logger.print("Issue Number: ", issue_number)
        Settings.logger.print("Issue Title: ", issue_title)
        r_issue = Settings.logger.confirm("Is this issue related to the commit?")
        if r_issue:
            commit_message += f" (issue: #{issue_number})"
        else:
            issue_number = None

        if issue_number is None and issue_markdown:
            commit_message = handle_issue_markdown(commit_message, issue_markdown)

    return commit_message


def handle_issue_markdown(commit_message: str, issue_markdown: str) -> str:
    md = Markdown(issue_markdown)
    Settings.logger.print(md)
    validate_issue = True
    issue_number = None
    while validate_issue:
        issue_number = input("Issue number?\nLeave blank if none: ").strip()
        if issue_number.startswith("#") and issue_number[1:].isdigit():
            issue_number = issue_number[1:]
            validate_issue = False
        elif issue_number.isdigit():
            validate_issue = False
        elif not issue_number:
            break
    if not validate_issue or not issue_number:
        commit_message += f" (issue: #{issue_number})"
    return commit_message


def get_issue_details(seeds):
    from pieces._vendor.pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
    from pieces._vendor.pieces_os_client.models.qgpt_relevance_input_options import (
        QGPTRelevanceInputOptions,
    )

    issue_prompt = """Please provide the issue number that is related to the changes, If nothing related write 'None'.
            `Output format WITHOUT ADDING ANYTHING ELSE: "Issue: **ISSUE NUMBER OR NONE HERE**`,
            `Example: 'Issue: 12', 'Issue: None'`,
            `Note: Don't provide any other information`
            `Here are the issues:`\n{issues}"""

    repo_details = get_git_repo_name()
    issues = get_repo_issues(*repo_details) if repo_details else []

    if issues:
        try:
            issue_markdown = format_issues_markdown(issues)
            issue_number = (
                Settings.pieces_client.qgpt_api.relevance(
                    QGPTRelevanceInput(
                        query=issue_prompt.format(issues=issue_markdown),
                        application=Settings.pieces_client.application.id,
                        model=Settings.get_auto_commit_model(),
                        options=QGPTRelevanceInputOptions(question=True),
                        seeds=seeds,
                    )
                )
                .answer.answers.iterable[0]  # This will raise AttributeError if none
                .text
            )

            issue_number = int(issue_number.replace("Issue: ", ""))
            issue_title = next(
                (
                    issue["title"]
                    for issue in issues
                    if issue["number"] == issue_number
                ),  # This will raise KeyError
                None,
            )
        except (AttributeError, KeyError, ValueError):
            issue_number = None
            issue_title = None
            issue_markdown = None
        return issue_number, issue_title, issue_markdown


def format_issues_markdown(issues: list) -> str:
    return "\n".join(
        (
            f"- `Issue_number: {issue['number']}`\n"
            f"`Title: {issue['title']}`\n"
            f"- `Body: {issue['body']}`"
        )
        for issue in issues
    )


def get_commit_message(changes_summary, seeds):
    from pieces._vendor.pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
    from pieces._vendor.pieces_os_client.models.qgpt_relevance_input_options import (
        QGPTRelevanceInputOptions,
    )

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
        commit_message = (
            Settings.pieces_client.qgpt_api.relevance(
                QGPTRelevanceInput(
                    query=message_prompt,
                    seeds=seeds,
                    application=Settings.pieces_client.application.id,
                    model=Settings.get_auto_commit_model(),
                    options=QGPTRelevanceInputOptions(question=True),
                )
            )
            .answer.answers.iterable[0]
            .text
        )

        commit_message = clean_commit_message(commit_message)
    except AttributeError as e:
        Settings.show_error("Failed to get the response from the LLM model")
        Settings.logger.critical(f"Faild to get the .answer.answers from the model {e}")
        return
    except Exception as e:
        Settings.show_error("Error in getting the commit message", e)
        Settings.logger.critical(e)
        return
    return commit_message


def clean_commit_message(commit_message: str) -> str:
    commit_message = commit_message.replace("The message is:", "", 1)
    commit_message = commit_message.replace("*", "")
    commit_message = commit_message.replace("__", "")
    return commit_message.strip()
