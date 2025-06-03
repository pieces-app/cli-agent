from enum import Enum
import webbrowser
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl


class URLs(Enum):
    DOCS_INSTALLATION = "https://docs.pieces.app/products/meet-pieces/fundamentals"
    DOCS_CLI = "https://docs.pieces.app/products/cli"
    PIECES_APP_WEBSITE = "https://pieces.app"
    PIECES_CLI_REPO = "https://github.com/pieces-app/cli-agent"
    PIECES_CLI_ISSUES = "https://github.com/pieces-app/cli-agent/issues"
    PIECES_CLI_FEEDBACK_DISCUSSION = (
        "https://github.com/pieces-app/cli-agent/discussions/194"
    )
    PIECES_OS_DOWNLOAD_WINDOWS = "https://builds.pieces.app/stages/production/appinstaller/os_server.appinstaller?product=PIECES_FOR_DEVELOPERS_CLI&download=true"
    PIECES_OS_DOWNLOAD_LINUX = "https://snapcraft.io/pieces-os"
    PIECES_OS_DOWNLOAD_MACOS_X86 = (
        "https://builds.pieces.app/stages/production/macos_packaging/pkg-pos-launch-only"
        "/download?product=PIECES_FOR_DEVELOPERS_CLI&download=true"
    )
    PIECES_OS_DOWNLOAD_MACOS_ARM64 = (
        "https://builds.pieces.app/stages/production/macos_packaging/pkg-pos-launch-only-arm64"
        "/download?product=PIECES_FOR_DEVELOPERS_CLI&download=true"
    )
    CURSOR_DOCS = (
        "https://docs.pieces.app/products/mcp/cursor#using-pieces-mcp-server-in-cursor"
    )
    VS_CODE_DOCS = "https://docs.pieces.app/products/mcp/github-copilot#using-pieces-mcp-server-in-github-copilot"
    GOOSE_DOCS = (
        "https://docs.pieces.app/products/mcp/goose#using-pieces-mcp-server-in-goose"
    )
    CLAUDE_DOCS = (
        "https://modelcontextprotocol.io/quickstart/user#1-download-claude-for-desktop"
    )

    # MCP Command Documentation URLs
    CLI_MCP_DOCS = "https://docs.pieces.app/products/mcp"
    CLI_MCP_SETUP_DOCS = "https://docs.pieces.app/products/mcp#setup"
    CLI_MCP_LIST_DOCS = "https://docs.pieces.app/products/mcp#list"
    CLI_MCP_DOCS_COMMAND = "https://docs.pieces.app/products/mcp#docs"
    CLI_MCP_START_DOCS = "https://docs.pieces.app/products/mcp#start"
    CLI_MCP_REPAIR_DOCS = "https://docs.pieces.app/products/mcp#repair"
    CLI_MCP_STATUS_DOCS = "https://docs.pieces.app/products/mcp#status"

    # CLI Command Documentation URLs
    CLI_VERSION_DOCS = "https://docs.pieces.app/products/cli#version"
    CLI_LIST_DOCS = "https://docs.pieces.app/products/cli#list"
    CLI_CONFIG_DOCS = "https://docs.pieces.app/products/cli#config"
    CLI_SAVE_DOCS = "https://docs.pieces.app/products/cli#save"
    CLI_DELETE_DOCS = "https://docs.pieces.app/products/cli#delete"
    CLI_CREATE_DOCS = "https://docs.pieces.app/products/cli#create"
    CLI_SHARE_DOCS = "https://docs.pieces.app/products/cli#share"
    CLI_RUN_DOCS = "https://docs.pieces.app/products/cli#run"
    CLI_EXECUTE_DOCS = "https://docs.pieces.app/products/cli#execute"
    CLI_EDIT_DOCS = "https://docs.pieces.app/products/cli#edit"
    CLI_ASK_DOCS = "https://docs.pieces.app/products/cli#ask"
    CLI_SEARCH_DOCS = "https://docs.pieces.app/products/cli#search"
    CLI_LOGIN_DOCS = "https://docs.pieces.app/products/cli#login"
    CLI_LOGOUT_DOCS = "https://docs.pieces.app/products/cli#logout"
    CLI_CHATS_DOCS = "https://docs.pieces.app/products/cli#chats"
    CLI_CHAT_DOCS = "https://docs.pieces.app/products/cli#chat"
    CLI_COMMIT_DOCS = "https://docs.pieces.app/products/cli#commit"
    CLI_ONBOARDING_DOCS = "https://docs.pieces.app/products/cli#onboarding"
    CLI_FEEDBACK_DOCS = "https://docs.pieces.app/products/cli#feedback"
    CLI_CONTRIBUTE_DOCS = "https://docs.pieces.app/products/cli#contribute"
    CLI_INSTALL_DOCS = "https://docs.pieces.app/products/cli#install"
    CLI_OPEN_DOCS = "https://docs.pieces.app/products/cli#open"
    CLI_HELP_DOCS = "https://docs.pieces.app/products/cli#help"

    def open_website(self):
        from pieces.settings import Settings

        url = self.value
        if hasattr(Settings.pieces_client, "user_api"):
            user_profile = Settings.pieces_client.user_api.user_snapshot().user
            if (not Settings.pieces_client.is_pieces_running) or (
                "pieces.app" not in url
            ):
                return webbrowser.open(url)
            para = {}
            if user_profile:
                para["user"] = user_profile.id
            _id = Settings.get_os_id()
            if _id:
                para["os"] = _id

            url_parts = list(urlparse(url))
            query = dict(parse_qsl(url_parts[4]))
            query.update(para)

            url_parts[4] = urlencode(query)
            new_url = urlunparse(url_parts)
        else:
            new_url = url
        try:
            webbrowser.open(new_url)
        except Exception as e:
            Settings.logger.print(f"Failed to open link: {e}")
