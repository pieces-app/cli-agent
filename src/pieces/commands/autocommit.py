import subprocess
import re

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
    truncated_summary = " ".join(words[:word_limit])
    return truncated_summary


def git_commit(**kwargs):
    from .commands_functions import ws_manager,model_id,word_limit # just make sure the model id is already updated
    changes_summary = get_current_working_changes(word_limit)
    prompt = f"Generate a github commit message for a Python CLI tool based on the following changes.Remember to follow the git commit message best practices:\n{changes_summary}"
    commit_message = ws_manager.ask_question(model_id,prompt,False)
    print(f"The generated commit message is:\n {commit_message}")
    r = input("Are you sure you want commit these changes? (y/n): ")
    if r.lower() == "y":
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            print("Successfully committed with message:", commit_message)
        except subprocess.CalledProcessError as e:
            print("Failed to commit changes:", e)
    else:
        print("Committing changes cancelled")
