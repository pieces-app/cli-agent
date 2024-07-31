import unittest
from unittest.mock import patch, MagicMock, call, ANY
from pieces.autocommit.autocommit import git_commit, get_current_working_changes, get_issue_details, create_seeded_asset
from pieces.settings import Settings
from pieces_os_client.models.seeds import Seeds
from pieces.gui import show_error

class TestGitCommit(unittest.TestCase):
    def setUp(self):
        Settings.startup()
        self.mock_get_git_repo_name = patch('pieces.autocommit.autocommit.get_git_repo_name').start()
        self.mock_get_git_repo_name.return_value = ('username', 'repo')
        
        self.mock_get_repo_issues = patch('pieces.autocommit.autocommit.get_repo_issues').start()
        self.mock_get_repo_issues.return_value = [{'title': 'issue1', 'number': 1, 'body': 'issue body'}]
        
        self.mock_qgpt_api = patch('pieces_os_client.api.qgpt_api.QGPTApi').start()
        mock_answer = MagicMock()
        mock_answer.text = 'feat: add new test cases for user authentication'
        mock_api_response = MagicMock()
        mock_api_response.answer.answers.iterable = [mock_answer]
        self.mock_qgpt_api.return_value.relevance.return_value = mock_api_response
        
        self.mock_get_changes = patch('pieces.autocommit.autocommit.get_current_working_changes').start()
        self.mock_get_changes.return_value = ('Test changes summary', Seeds(iterable=[
            create_seeded_asset("/path/to/file1.py", "content1"),
            create_seeded_asset("/path/to/file2.py", "content2")
        ]))
        
        self.mock_input = patch('builtins.input').start()
        self.mock_input.side_effect = ['y', '']  # Default inputs
        
        self.mock_subprocess = patch('subprocess.run').start()
        
        self.mock_show_error = patch('pieces.gui.show_error').start()
