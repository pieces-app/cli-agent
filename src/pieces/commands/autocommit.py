import subprocess
import re
from pieces.gui import show_error
from pieces.api.config import pos_client,api_client
import re

def get_current_working_changes(word_limit:int=2000) -> str:
    """
    Fetches the detailed changes in the files you are currently working on, limited to a specific word count.
    
    Args:
        word_limit (int): The maximum number of words to include in the summary.
    
    Returns:
        A string summarizing the detailed changes in a format suitable for generating commit messages,
        truncated to the specified word limit.
    """
    
    result = subprocess.run(["git", "diff"], capture_output=True, text=True)
    detailed_diff = result.stdout.strip()
    
    summary = ""
    for line in detailed_diff.split('\n'):
        if line.startswith('diff --git'):
            file_changed = re.search(r'diff --git a/(.+) b/\1', line)
            if file_changed.group(1).endswith("poetry.lock"):
                continue
            if file_changed:
                summary += f"File changed: **{file_changed.group(1)}**\n"
        elif line.startswith('+') and not line.startswith('+++'):
            summary += "Addition: " + line[1:].strip() + "\n"
        elif line.startswith('-') and not line.startswith('---'):
            summary += "Deletion: " + line[1:].strip() + "\n"
    
    
    # Truncate the summary to the specified word limit
    truncated_summary = summary[:word_limit-340] # removeing 340 characters because of the prompt characters
    return truncated_summary


def git_commit(**kwargs):
    from .commands_functions import ws_manager,model_id,word_limit # just make sure the model id is already updated
    changes_summary = get_current_working_changes(word_limit)
    prompt = f"""Generate a concise git commit message written in present tense for the following code diff with the given specifications below:',
		`Message language: English`,
		`Commit message must be a maximum of 72 characters.`,
		`Exclude anything unnecessary such as translation, your git commit. Your entire response will be passed directly into git commit without **any edits**`,
        Here are the changes lists:\n{changes_summary}"""
    try:
        commit_message = ws_manager.ask_question(model_id,prompt,False)
        # Remove extras
        # Remove leading and trailing quotes
        commit_message = re.sub(r'^["\']|["\']$', '', commit_message)

        # Remove markdown code block syntax
        commit_message = re.sub(r'^```|```$', '', commit_message)

        # Remove leading 'plaintext'
        commit_message = re.sub(r'^plaintext', '', commit_message)

        # Remove leading and trailing whitespace
        commit_message = commit_message.strip()
        pos_client.ConversationsApi(api_client).conversations_delete_specific_conversation(conversation=ws_manager.conversation)
        ws_manager.conversation = None
    except Exception as e:
        show_error("Error in getting the commit message",e)
        return
    print(f"The generated commit message is: {commit_message}")
    r = input("Are you sure you want commit these changes? (y/n): ")
    if r.lower() == "y":
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            print("Successfully committed with message:", commit_message)
        except subprocess.CalledProcessError as e:
            print("Failed to commit changes:", e)
        if kwargs["push"]:
            subprocess.run(["git", "push"], check=True)
    else:
        print("Committing changes cancelled")