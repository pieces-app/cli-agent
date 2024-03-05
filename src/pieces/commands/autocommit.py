import subprocess
import re
import sys
from pieces.gui import show_error

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
    truncated_summary = " ".join(words[:word_limit-230]) # removeing 230 characters because of the prompt
    return truncated_summary


def git_commit(**kwargs):
    from .commands_functions import ws_manager,model_id,word_limit # just make sure the model id is already updated
    changes_summary = get_current_working_changes(word_limit)
    prompt = f"Generate a github commit message for a Python CLI tool based on the following changes.Remember to follow the git commit message best practices and don't exceed 72 character and your answer must be between two quotes in one sentence :\n{changes_summary}"
    try:
        commit_message = ws_manager.ask_question(model_id,prompt,False)
        # remove extras
        commit_message = commit_message[1:] if commit_message.startswith('"') or commit_message.startswith("'") else commit_message 
        commit_message = commit_message[:-1] if commit_message.endswith('"') or commit_message.endswith("'") else commit_message
        commit_message = commit_message[3:] if commit_message.startswith("```") else commit_message 
        commit_message = commit_message[:-3] if commit_message.endswith('```') else commit_message
        commit_message = commit_message[9:] if commit_message.startswith("plaintext") else commit_message 
        commit_message = commit_message.strip()
        
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