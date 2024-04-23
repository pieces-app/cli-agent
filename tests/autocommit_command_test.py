import unittest
from unittest.mock import patch
from pieces.commands.autocommit.autocommit import git_commit
from pieces.commands import startup

class TestGitCommit(unittest.TestCase):
    @patch('pieces.commands.autocommit.autocommit.subprocess.run')
    @patch('pieces.commands.autocommit.autocommit.get_current_working_changes')
    @patch('pieces.commands.autocommit.autocommit.get_repo_issues')
    @patch('pieces.commands.autocommit.autocommit.pos_client.QGPTApi')
    @patch('pieces.commands.autocommit.autocommit.get_git_repo_name')
    @patch('builtins.input', return_value='y')
    def test_git_commit(self,mock_input,mock_qgpt_api, mock_get_repo_name, mock_get_issues, mock_get_changes, mock_subprocess):
        # TODO: Fix this test to give better results and test the commit command
        
        # Setup
        startup()
        # Setup
        mock_qgpt_api.return_value.relevance.return_value.answer.answers.iterable[0].text = 'test: implement changes according to summary'
        
        # Rest of your test code
        mock_get_repo_name.return_value = ('username', 'repo')
        mock_get_issues.return_value = [{'title': 'issue1', 'number': 1, 'body': 'issue body'}]
        mock_get_changes.return_value = ('Test changes summary', ['file1', 'file2'])
        mock_subprocess.return_value = None  # Assuming subprocess.run doesn't return anything useful for the test

        # Call the function with issue_flag=False, push=False
        git_commit(issue_flag=False, push=False)

        # Check that the get_repo_issues was not called
        mock_get_issues.assert_not_called()

        # Check that the subprocess.run was called with the expected arguments
        mock_subprocess.assert_called_once_with(["git", "commit", "-m", 'test: implement changes according to summary'], check=True)

        # Call the function with issue_flag=True, push=False
        git_commit(issue_flag=True, push=False)

        # Check that the get_repo_issues was called
        mock_get_issues.assert_called_once_with('username', 'repo')

        # Check that the subprocess.run was called with the expected arguments
        mock_subprocess.assert_called_with(["git", "commit", "-m", 'Test changes summary (issue: #1)'], check=True)

        # Call the function with issue_flag=False, push=True
        git_commit(issue_flag=False, push=True)

        # Check that the subprocess.run was called with the expected arguments for git push
        mock_subprocess.assert_called_with(["git", "push"], check=True)

        # Call the function with issue_flag=True, push=True
        git_commit(issue_flag=True, push=True)

        # Check that the subprocess.run was called with the expected arguments for git push
        mock_subprocess.assert_called_with(["git", "push"], check=True)

if __name__ == '__main__':
    unittest.main()