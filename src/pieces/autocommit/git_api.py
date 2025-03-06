import urllib.request
import json
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlencode
import subprocess
from pieces.settings import Settings


def get_git_repo_name() -> Optional[Tuple[str, str]]:
    """
    Retrieves the name of the git repository by executing a git command to get the remote origin URL. 

    Returns:
        A tuple containing a string representing the username and repository name.
    """
    try:
        try:
            # Get the remote origin URL of the git repository upstream url
            repo_url = subprocess.check_output(
                ["git", "config", "--get", "remote.upstream.url"]
            ).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            repo_url = subprocess.check_output(
                ["git", "config", "--get", "remote.origin.url"]
            ).decode('utf-8').strip()

        # Extract the username and repository name from the URL
        repo_info = repo_url.split('/')[-2:]
        username, repo_name = repo_info[0], repo_info[1].replace('.git', '')

        return username, repo_name
    except subprocess.CalledProcessError as e:
        Settings.show_error(f"Error retrieving git repository name: {e}")
        return None


def get_repo_issues(repo_owner: str, repo_name: str) -> List[Optional[Dict[str, str]]]:
    """
    This function searches for issues in a public GitHub repository using the search API.
    Args:
        repo_owner (str): The owner of the repository.
        repo_name (str): The name of the repository.
    Returns:
        list: A list of dictionaries of opened issues containing basic information about issues (number,title, body).
        Returns None if no issues are found.
    """
    params = {'q':
              f'is:issue is:open repo:{repo_owner}/{repo_name}',
              'per_page': '30'}
    query_string = urlencode(params)
    url = f"https://api.github.com/search/issues?{query_string}"

    req = urllib.request.Request(url=url)
    res = urllib.request.urlopen(req, timeout=10)
    data = json.loads(res.read().decode('utf-8'))

    if data.get('total_count', 0) == 0:
        return []

    # Extract issue titles and URLs from search results
    issues = []

    for item in data.get('items', []):
        # Skip closed issues
        if item['state'] != 'open':
            continue

        # Extract issue information
        issues.append({
            "title": item['title'],  # Issue title
            "number": item['number'],  # Issue number
            "body": item['body']  # Issue body (markdown)
        })

    return issues
