import pytest
from unittest.mock import patch, MagicMock
from pieces.mcp.handler import handle_mcp, handle_mcp_docs, handle_repair, handle_status
from pieces.settings import Settings


@pytest.fixture
def mock_settings():
    logger = Settings.logger.debug
    confirm = Settings.logger.confirm
    with patch("pieces.mcp.handler.Settings") as mock:
        mock.logger = MagicMock()
        mock.logger.debug = logger
        mock.logger.confirm = confirm
        mock.show_error = MagicMock()
        mock.open_website = MagicMock()
        yield mock


@pytest.fixture
def mock_input():
    with patch("builtins.input", return_value="y"):
        yield


@pytest.fixture
def mock_urlopen():
    with patch("urllib.request.urlopen") as mock:
        mock.return_value.__enter__.return_value = MagicMock()
        yield mock


def test_handle_mcp_server_not_running(mock_settings, mock_urlopen):
    mock_urlopen.side_effect = Exception("Connection refused")

    handle_mcp()

    mock_settings.show_error.assert_called_once()
    assert (
        "Pieces MCP server is not running" in mock_settings.show_error.call_args[0][0]
    )


def test_handle_mcp_docs_current(mock_settings):
    with patch("pieces.mcp.handler.supported_mcps") as mock_mcps:
        mock_mcps.items.return_value = [
            (
                "vscode",
                MagicMock(
                    is_set_up=lambda: True,
                    readable="VS Code",
                    docs_no_css_selector="vscode-docs",
                ),
            ),
            (
                "cursor",
                MagicMock(
                    is_set_up=lambda: True,
                    readable="Cursor",
                    docs_no_css_selector="cursor-docs",
                ),
            ),
        ]

        handle_mcp_docs("current")

        assert mock_settings.logger.print.call_count == 2


def test_handle_repair_all(mock_settings):
    with patch("pieces.mcp.handler.supported_mcps") as mock_mcps:
        vscode_mock = MagicMock()
        vscode_mock.need_repair.return_value = ["/path/to/vscode/settings.json"]
        vscode_mock.on_select = MagicMock()
        vscode_mock.readable = "VS Code"

        cursor_mock = MagicMock()
        cursor_mock.need_repair.return_value = ["/path/to/cursor/settings.json"]
        cursor_mock.on_select = MagicMock()
        cursor_mock.readable = "Cursor"
        goose_mock = MagicMock()

        # Set up the mock dictionary to be iterable
        mock_mcps.__iter__.return_value = iter(["vscode", "cursor", "goose"])
        mock_mcps.__getitem__.side_effect = lambda key: {
            "vscode": vscode_mock,
            "cursor": cursor_mock,
            "goose": goose_mock,
        }[key]

        handle_repair("all")

        vscode_mock.repair.assert_called_once()
        cursor_mock.repair.assert_called_once()


def test_handle_status_with_repair_needed(mock_settings, mock_input):
    with patch("pieces.mcp.handler.supported_mcps") as mock_mcps:
        mock_mcps.__getitem__.return_value.check_ltm.return_value = True

        vscode_mock = MagicMock()
        vscode_mock.need_repair.return_value = ["/path/to/vscode/settings.json"]
        vscode_mock.repair = MagicMock()
        vscode_mock.readable = "VS Code"

        cursor_mock = MagicMock()
        cursor_mock.need_repair.return_value = ["/path/to/cursor/settings.json"]
        cursor_mock.repair = MagicMock()
        cursor_mock.readable = "Cursor"

        mock_mcps.items.return_value = [
            ("vscode", vscode_mock),
            ("cursor", cursor_mock),
        ]

        handle_status()

        vscode_mock.need_repair.assert_called_once()
        cursor_mock.need_repair.assert_called_once()


def test_handle_status_no_repair_needed(mock_settings, mock_input):
    with patch("pieces.mcp.handler.supported_mcps") as mock_mcps:
        mock_mcps.__getitem__.return_value.check_ltm.return_value = True

        vscode_mock = MagicMock()
        vscode_mock.need_repair.return_value = []  # No paths need repair
        vscode_mock.repair = MagicMock()
        vscode_mock.readable = "VS Code"

        cursor_mock = MagicMock()
        cursor_mock.need_repair.return_value = []  # No paths need repair
        cursor_mock.repair = MagicMock()
        cursor_mock.readable = "Cursor"

        mock_mcps.items.return_value = [
            ("vscode", vscode_mock),
            ("cursor", cursor_mock),
        ]
        handle_status()

        vscode_mock.need_repair.assert_called_once()
        cursor_mock.need_repair.assert_called_once()

        vscode_mock.repair.assert_not_called()
        cursor_mock.repair.assert_not_called()


def test_handle_status_ltm_not_running(mock_settings):
    with patch("pieces.mcp.handler.supported_mcps") as mock_mcps:
        mock_mcps.__getitem__.return_value.check_ltm.return_value = False

        handle_status()

        mock_settings.logger.print.assert_called_with("[red]LTM is not running[/red]")
