import unittest
from unittest.mock import Mock, patch
from prompt_toolkit.application import Application
from prompt_toolkit.output import DummyOutput
from pieces.utils import PiecesSelectMenu


class TestPiecesSelectMenu(unittest.TestCase):
    def setUp(self):
        self.menu_options = [
            ("Option 1", "arg1"),
            ("Option 2", "arg2"),
            ("Option 3", "arg3"),
        ]
        self.on_enter_callback = Mock()
        self.select_menu = PiecesSelectMenu(
            self.menu_options, self.on_enter_callback, "Footer Text"
        )

    def test_initialization(self):
        self.assertEqual(self.select_menu.menu_options, self.menu_options)
        self.assertEqual(self.select_menu.current_selection, 0)
        self.assertEqual(self.select_menu.footer_text, "Footer Text")

    @patch("shutil.get_terminal_size")
    def test_update_visible_range(self, mock_get_terminal_size):
        mock_get_terminal_size.return_value = Mock(lines=10)
        self.select_menu.update_visible_range()
        self.assertEqual(self.select_menu.visible_start, 0)
        self.assertEqual(self.select_menu.visible_end, 3)

    def test_get_menu_text(self):
        menu_text = self.select_menu.get_menu_text()
        self.assertEqual(len(menu_text), 3)
        self.assertEqual(menu_text[0][0], "class:selected")
        self.assertEqual(menu_text[1][0], "class:unselected")
        self.assertEqual(menu_text[2][0], "class:unselected")

    @patch("prompt_toolkit.output.defaults.create_output")
    @patch.object(Application, "run")
    def test_run_with_string_arg(self, mock_run, mock_create_output):
        mock_create_output.return_value = DummyOutput()
        mock_run.return_value = "arg1"
        self.select_menu.run()
        self.on_enter_callback.assert_called_once_with("arg1")

    @patch("prompt_toolkit.output.defaults.create_output")
    @patch.object(Application, "run")
    def test_run_with_list_arg(self, mock_run, mock_create_output):
        mock_create_output.return_value = DummyOutput()
        mock_run.return_value = ["arg1", "arg2"]
        self.select_menu.run()
        self.on_enter_callback.assert_called_once_with("arg1", "arg2")

    @patch("prompt_toolkit.output.defaults.create_output")
    @patch.object(Application, "run")
    def test_run_with_dict_arg(self, mock_run, mock_create_output):
        mock_create_output.return_value = DummyOutput()
        mock_run.return_value = {"key": "value"}
        self.select_menu.run()
        self.on_enter_callback.assert_called_once_with(key="value")


if __name__ == "__main__":
    unittest.main()
