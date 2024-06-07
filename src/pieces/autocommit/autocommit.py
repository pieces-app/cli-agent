import subprocess
import re
from .git_api import get_repo_issues
from typing import Optional,Tuple
from pieces.settings import Settings
from pieces.gui import show_error
import os
from collections import defaultdict 
from rich.console import Console
from rich.markdown import Markdown

from pieces_os_client.api.qgpt_api import QGPTApi
from pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
from pieces_os_client.models.qgpt_relevance_input_options import QGPTRelevanceInputOptions
from pieces_os_client.models.seeds import Seeds
from pieces_os_client.models.seed import Seed
from pieces_os_client.models.classification_specific_enum import ClassificationSpecificEnum
from pieces_os_client.models.seeded_asset import SeededAsset
from pieces_os_client.models.seeded_format import SeededFormat
from pieces_os_client.models.seeded_fragment import SeededFragment
from pieces_os_client.models.transferable_string import TransferableString
from pieces_os_client.models.seeded_asset_metadata import SeededAssetMetadata
from pieces_os_client.models.anchor_type_enum import AnchorTypeEnum
from pieces_os_client.models.seeded_anchor import SeededAnchor

def get_git_repo_name() -> Optional[Tuple[str]]:
    """
    Retrieves the name of the git repository by executing a git command to get the remote origin URL. 
    
    Returns:
        A tuple containing a string representing the username and repository name.
    """
    try:
        try:
            # Get the remote origin URL of the git repository upstream url
            repo_url = subprocess.check_output(["git", "config", "--get", "remote.upstream.url"]).decode('utf-8').strip()

        except:
            repo_url = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).decode('utf-8').strip()
            
        # Extract the username and repository name from the URL
        repo_info = repo_url.split('/')[-2:]
        username, repo_name = repo_info[0], repo_info[1].replace('.git', '')
        

        # Return the username and repository name
        return username, repo_name
    except:
        return None

def get_current_working_changes() -> Optional[Tuple[str,list]]:
    """
    Fetches the detailed changes in the files you are currently working on, limited to a specific word count.
    
    Returns:
        Tuple of
            A string summarizing the detailed changes in a format suitable for generating commit messages.
            List of seeded asset to be input to the relevence

    """
    
    result = subprocess.run(["git", "diff","--staged"], capture_output=True, text=True)
    if not result.stdout.strip():
        show_error("No changes found","Please make sure you have added some files to your staging area")
        return 
    detailed_diff = result.stdout.strip()
    
    # Create a summary of the changes
    summary = ""
    content_file = defaultdict(str)  # {file path : changes of the file}
    lines_diff = detailed_diff.split("\n")

    for idx,line in enumerate(lines_diff):
        if line.startswith('diff --git'):
            file_changed = re.search(r'diff --git a/(.+) b/\1', line)
            if file_changed:
                file_name = file_changed.group(1)
                if lines_diff[idx+1] == "new file mode 100644":
                    summary += f"File created: **{file_name}**\n"
                elif lines_diff[idx+1] == "deleted file mode 100644":
                    summary += f"File deleted: **{file_name}**\n"
                else:
                    summary += f"File modified: **{file_name}**\n"
        if (line.startswith('+') and not line.startswith('+++')) or (line.startswith('-') and not line.startswith('---')):
            
            content_file[os.path.join(os.getcwd(),*file_name.split("/"))] += line.strip()

    return summary,Seeds(iterable=[
        create_seeded_asset(file_path,content) for file_path,content in content_file.items()
    ]) # Create seed for each new file


def create_seeded_asset(file_path:str,content:str) -> Seed:
    return Seed(
			asset=SeededAsset(
				application=Settings.application,
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

    

def git_commit(**kwargs):
    if kwargs.get("all_flag",False):
        subprocess.run(["git", "add", "-A"], check=True)

    issue_flag = kwargs.get('issue_flag')
    try:
        changes_summary,seeds = get_current_working_changes()
    except TypeError:
        return

    commit_message = get_commit_message(changes_summary,seeds)
    if not commit_message: # Error in the commit message
        return
    
    if issue_flag:
        try:
            issue_number,issue_title,issue_markdown = get_issue_details(seeds)
        except TypeError: # Returned none 
            issue_flag = False

    # Check if the user wants to commit the changes or change the commit message
    r_message = input(f"The generated commit message is:\n\n {commit_message}\n\nAre you sure you want to commit these changes?\n\n- y: Yes\n- n: No\n- c: Change the commit message\n\nPlease enter your choice (y/n/c): ").lower().strip()
    
    if r_message == "y" or r_message == "c" or not r_message: # Accept by default if the user did not write anything 
        # Changing the commit message if the user wants to
        if r_message == "c":
            edit = input(f"Enter the new commit message [generated message is: '{commit_message}']: ")
            if edit:
                commit_message = edit

        if issue_flag:
            # Adding the Issue number if the user accept it
            if issue_number:
                print("Issue Number: ", issue_number)
                print("Issue Title: ", issue_title)
                r_issue = input("Is this issue related to the commit? (y/n): ")
                if r_issue.lower() == "y":
                    commit_message += f" (issue: #{issue_number})"
                else:
                    issue_number = None
            # Print the issues if we cant find the issie
            if issue_number == None and issue_markdown:
                console = Console()
                md = Markdown(issue_markdown)
                console.print(md)
                validate_issue = True
                while validate_issue:
                    issue_number = input("Issue number?\nLeave blanck if none: ").strip()
                    if issue_number.startswith("#") and issue_number[1:].isdigit():
                        issue_number = issue_number[1:]
                        validate_issue = False
                    elif issue_number.isdigit():
                        validate_issue = False
                    elif issue_number == None or issue_number == "":
                        break
                if not validate_issue:
                    commit_message += f" (issue: #{issue_number})"

        try:
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            print("Successfully committed with message:", commit_message)
            if kwargs.get('push',False):
                subprocess.run(["git", "push"])
        except subprocess.CalledProcessError as e:
            print("Failed to commit changes:", e)
        
    else:
        print("Committing changes cancelled")

def get_issue_details(seeds):
    issue_prompt = """Please provide the issue number that is related to the changes, If nothing related write 'None'.
            `Output format WITHOUT ADDING ANYTHING ELSE: "Issue: **ISSUE NUMBER OR NONE HERE**`,
            `Example: 'Issue: 12', 'Issue: None'`,
            `Note: Don't provide any other information`
            `Here are the issues:`\n{issues}"""
    
    # Issues
    repo_details = get_git_repo_name()
    issues = get_repo_issues(*repo_details) if repo_details else [] # Check if we got a vaild repo name

    if issues:
        try:
            # Make the issues look nicer
            issue_markdown = [
                f"- `Issue_number: {issue['number']}`\n- `Title: {issue['title']}`\n- `Body: {issue['body']}`"
                for issue in issues
            ]
            issue_markdown = "\n".join(issue_markdown) # To string
            issue_number = QGPTApi(Settings.api_client).relevance(
                    QGPTRelevanceInput(
                        query=issue_prompt.format(issues=issue_markdown),
                        application=Settings.application.id,
                        model=Settings.model_id,
                        options=QGPTRelevanceInputOptions(question=True),
                        seeds=seeds
                    )).answer.answers.iterable[0].text
    
            
            # Extract the issue part
            issue_number = issue_number.replace("Issue: ", "") 
            # If the issue is a number 
            issue_number = int(issue_number)
            issue_title = next((issue["title"] for issue in issues if issue["number"] == issue_number), None)
        except: 
            issue_number = None
            issue_title = ""
        return issue_number,issue_title,issue_markdown
    

def get_commit_message(changes_summary,seeds):
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
        commit_message = QGPTApi(Settings.api_client).relevance(
            QGPTRelevanceInput(
                query=message_prompt,
                seeds=seeds,
                application=Settings.application.id,
                model=Settings.model_id,
                options=QGPTRelevanceInputOptions(question=True)
            )).answer.answers.iterable[0].text 
        
        # Remove extras from the commit message
        commit_message = commit_message.replace("The message is:","",1) # Remove the "message is" part as mentioned in the prompt
        commit_message = commit_message.replace('*', '') # Remove the bold and italic characters
        commit_message = commit_message.replace('__', '') # Remove the bold and italic characters
        # Remove leading and trailing whitespace
        commit_message = commit_message.strip()
    except Exception as e:
        print("Error in getting the commit message",e)
        return
    return commit_message