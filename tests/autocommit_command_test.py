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

    def tearDown(self):
        patch.stopall()

    #Test 1 : git_commit_basic
    def test_git_commit_basic(self):
        git_commit(issue_flag=False, push=False)
        self.mock_subprocess.assert_called_with(["git", "commit", "-m", ANY], check=True)
        commit_message = self.mock_subprocess.call_args[0][0][3]
        self.assertIn("feat:", commit_message)
        self.assertIn("add new", commit_message)
        self.assertIn("authentication", commit_message)

    #Test 2 : git_commit_with_issue
    def test_git_commit_with_issue(self):
        self.mock_input.side_effect = ['y', 'y', '1', 'y']
        git_commit(issue_flag=True, push=False)
        self.mock_subprocess.assert_called_with(["git", "commit", "-m", ANY], check=True)
        commit_message = self.mock_subprocess.call_args[0][0][3]
        self.assertIn("feat:", commit_message)
        self.assertIn("add new", commit_message)
        self.assertIn("authentication", commit_message)
        self.assertIn("(issue: #1)", commit_message)

    #Test 3 : git_commit_with_push
    def test_git_commit_with_push(self):
        git_commit(issue_flag=False, push=True)
        self.mock_subprocess.assert_has_calls([
            call(["git", "commit", "-m", ANY], check=True),
            call(["git", "push"])
        ])
        commit_message = self.mock_subprocess.call_args_list[0][0][0][3]
        self.assertIn("feat:", commit_message)
        self.assertIn("add new", commit_message)
        self.assertIn("authentication", commit_message)

    #Test 4 : git_commit_change_message
    def test_git_commit_change_message(self):
        self.mock_input.side_effect = ['c', 'new commit message', 'y']
        git_commit(issue_flag=False, push=False)
        self.mock_subprocess.assert_called_with(["git", "commit", "-m", 'new commit message'], check=True)

    #Test 5 : git_commit_cancel
    def test_git_commit_cancel(self):
        self.mock_input.side_effect = ['n']
        git_commit(issue_flag=False, push=False)
        self.mock_subprocess.assert_not_called()

    #Test 6 : git_commit_all_flag
    def test_git_commit_all_flag(self):
        git_commit(all_flag=True, issue_flag=False, push=False)
        self.mock_subprocess.assert_has_calls([
            call(["git", "add", "-A"], check=True),
            call(["git", "commit", "-m", ANY], check=True)
        ])
        commit_message = self.mock_subprocess.call_args_list[1][0][0][3]
        self.assertIn("feat:", commit_message)
        self.assertIn("add new", commit_message)
        self.assertIn("authentication", commit_message)

    #Test 7 : git_commit_no_related_issue
    @patch('pieces.autocommit.autocommit.get_issue_details')
    def test_git_commit_no_related_issue(self, mock_get_issue_details):
        mock_get_issue_details.return_value = (None, None, "Issue markdown")
        self.mock_input.side_effect = ['y', '']
        git_commit(issue_flag=True, push=False)
        self.mock_subprocess.assert_called_with(["git", "commit", "-m", ANY], check=True)
        commit_message = self.mock_subprocess.call_args[0][0][3]
        self.assertIn("feat:", commit_message)
        self.assertIn("add new", commit_message)
        self.assertIn("authentication", commit_message)

    #Test 8 : git_commit_no_changes
    def test_git_commit_no_changes(self):
        self.mock_get_changes.return_value = (None, None)
        git_commit(issue_flag=False, push=False)
        print(".No changes found")

    #Test 9 : get_current_working_changes
    def test_get_current_working_changes(self):
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(stdout="diff --git a/file1.py b/file1.py\n+new line\n-old line")
            summary, seeds = get_current_working_changes()
            self.assertIn("File modified: **file1.py**", summary)
            self.assertIsInstance(seeds, Seeds)
            self.assertEqual(len(seeds.iterable), 1)

    #Test 10 : get_issue_details
    @patch('pieces.autocommit.autocommit.QGPTApi')
    def test_get_issue_details(self, mock_qgpt_api):
        mock_answer = MagicMock()
        mock_answer.text = 'Issue: 1'
        mock_api_response = MagicMock()
        mock_api_response.answer.answers.iterable = [mock_answer]
        mock_qgpt_api.return_value.relevance.return_value = mock_api_response

        seeds = Seeds(iterable=[create_seeded_asset("/path/to/file1.py", "content1")])
        issue_number, issue_title, issue_markdown = get_issue_details(seeds)

        self.assertEqual(issue_number, 1)
        self.assertEqual(issue_title, "issue1")
        self.assertIn("Issue_number: 1", issue_markdown)

if __name__ == '__main__':
    unittest.main()
