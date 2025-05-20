from unittest.mock import patch, Mock
from io import StringIO
import sys
from tests.conftest import SCRIPT_NAME


def run_main_with_args(args, main_func):
    args.insert(0, SCRIPT_NAME)
    with patch("sys.argv", args):
        main_func()


def capture_stderr():
    original_stderr = sys.stderr
    sys.stderr = StringIO()
    return original_stderr


def restore_stderr(original_stderr):
    sys.stderr = original_stderr


def mock_select_menus(
    main_func,
    module,
    expected_select_options,
    expected_footer,
    expected_on_enter,
    add_entry_calls=None,
):
    with patch(f"{module}.PiecesSelectMenu") as mock_menu:
        add_entry_mock = Mock()
        mock_menu.add_entry = add_entry_mock
        main_func()
        # Check that PiecesSelectMenu was called with the expected arguments
        mock_menu.assert_called_once()

        actual_select_options, actual_on_enter, actual_footer = mock_menu.call_args.args
        assert actual_footer == expected_footer
        assert actual_on_enter == expected_on_enter

        if actual_select_options and expected_select_options:
            actual_list_items, actual_args_used = zip(*actual_select_options)
            expected_list_items, expected_args_used = zip(*expected_select_options)
            assert actual_list_items == expected_list_items

            for idx in range(len(expected_args_used)):
                for key, val in expected_args_used[idx].items():
                    assert actual_args_used[idx][key] == val

        # if add_entry_calls:
        #     assert add_entry_mock.call_count == len(add_entry_calls)
        #     for call in add_entry_calls:
        #         add_entry_mock.assert_has_calls(call, any_order=True)
