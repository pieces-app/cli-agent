import subprocess
import re
import sys
from pieces.gui import show_error
from pieces.api.config import pos_client,api_client

def get_current_working_changes(word_limit=2000):
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
    
    changes_summary = []
    
    for line in detailed_diff.split('\n'):
        if line.startswith('diff --git'):
            file_changed = re.search(r'diff --git a/(.+) b/\1', line)
            if file_changed.group(1).endswith("poetry.lock"):
                continue
            if file_changed:
                changes_summary.append(f"Modified {file_changed.group(1)}")
        elif line.startswith('+') and not line.startswith('+++'):
            changes_summary.append("Addition: " + line[1:].strip())
        elif line.startswith('-') and not line.startswith('---'):
            changes_summary.append("Deletion: " + line[1:].strip())
    
    summary_text = " ".join(changes_summary)
    words = summary_text.split()
    
    # Truncate the summary to the specified word limit
    truncated_summary = " ".join(words[:word_limit-340]) # removeing 340 characters because of the prompt
    return truncated_summary


def git_commit(**kwargs):
    from .commands_functions import ws_manager,model_id,word_limit # just make sure the model id is already updated
    changes_summary = get_current_working_changes(word_limit)
    prompt = f"""Generate a concise git commit message written in present tense for the following code diff with the given specifications below:',
		`Message language: English`,
		`Commit message must be a maximum of 72 characters.`,
		`Exclude anything unnecessary such as translation. Your entire response will be passed directly into git commit`,
        Here are the changes lists:\n{changes_summary}"""
    try:
        commit_message = ws_manager.ask_question(model_id,prompt,False)
        commit_message = commit_message[1:-1] if commit_message.startswith('"') or commit_message.endswith("'") else commit_message
        commit_message.replace("``` plaintext ","")
        commit_message.replace("```","")

        res = pos_client.ConversationsApi(api_client).conversations_delete_specific_conversation_with_http_info(conversation=ws_manager.conversation)
        ws_manager.conversation = None
        print(res)
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