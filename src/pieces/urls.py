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
    CURSOR_MCP_DOCS = (
        "https://docs.pieces.app/products/mcp/cursor#using-pieces-mcp-server-in-cursor"
    )
    VS_CODE_MCP_DOCS = "https://docs.pieces.app/products/mcp/github-copilot#using-pieces-mcp-server-in-github-copilot"
    GOOSE_MCP_DOCS = (
        "https://docs.pieces.app/products/mcp/goose#using-pieces-mcp-server-in-goose"
    )
    CLAUDE_MCP_DOCS = (
        "https://modelcontextprotocol.io/quickstart/user#1-download-claude-for-desktop"
    )
    WINDSURF_MCP_DOCS = (
        "https://docs.windsurf.com/windsurf/cascade/mcp#model-context-protocol-mcp"
    )
    ZED_MCP_DOCS = "https://zed.dev/docs/ai/mcp"
    RAYCAST_MCP_DOCS = "https://manual.raycast.com/model-context-protocol"
    WRAP_MCP_DOCS = "https://docs.warp.dev/knowledge-and-collaboration/mcp"
    SHORT_WAVE_MCP_DOCS = "https://www.shortwave.com/docs/how-tos/using-mcp/"
    CLAUDE_CLI_MCP_DOCS = "https://docs.anthropic.com/en/docs/claude-code/mcp"

    # MCP Command Documentation URLs
    CLI_MCP_DOCS = "https://docs.pieces.app/products/cli/copilot/chat#pieces-mcp"
    CLI_MCP_SETUP_DOCS = "https://docs.pieces.app/products/cli/copilot/chat#setup"
    CLI_MCP_LIST_DOCS = "https://docs.pieces.app/products/cli/copilot/chat#list"
    CLI_MCP_DOCS_COMMAND = "https://docs.pieces.app/products/cli/copilot/chat#docs"
    CLI_MCP_START_DOCS = ""
    CLI_MCP_REPAIR_DOCS = "https://docs.pieces.app/products/cli/copilot/chat#repair"
    CLI_MCP_STATUS_DOCS = "https://docs.pieces.app/products/cli/copilot/chat#status"

    # CLI Command Documentation URLs
    CLI_VERSION_DOCS = "https://docs.pieces.app/products/cli/commands#version"
    CLI_LIST_DOCS = "https://docs.pieces.app/products/cli/commands#list"
    CLI_CONFIG_DOCS = "https://docs.pieces.app/products/cli/configuration"
    CLI_SAVE_DOCS = "https://docs.pieces.app/products/cli/drive/saving-materials"
    CLI_DELETE_DOCS = "https://docs.pieces.app/products/cli/commands#delete"
    CLI_CREATE_DOCS = "https://docs.pieces.app/products/cli/commands#create"
    CLI_SHARE_DOCS = "https://docs.pieces.app/products/cli/commands#share"
    CLI_RUN_DOCS = "https://docs.pieces.app/products/cli/commands#run"
    CLI_EXECUTE_DOCS = "https://docs.pieces.app/products/cli/commands#execute"
    CLI_EDIT_DOCS = "https://docs.pieces.app/products/cli/commands#edit"
    CLI_ASK_DOCS = (
        "https://docs.pieces.app/products/cli/commands#ask-your_question_here"
    )
    CLI_SEARCH_DOCS = "https://docs.pieces.app/products/cli/commands#search"
    CLI_LOGIN_DOCS = "https://docs.pieces.app/products/cli/commands#login"
    CLI_LOGOUT_DOCS = "https://docs.pieces.app/products/cli/commands#logout"
    CLI_CHATS_DOCS = "https://docs.pieces.app/products/cli/commands#chats"
    CLI_CHAT_DOCS = "https://docs.pieces.app/products/cli/commands#chat"
    CLI_COMMIT_DOCS = "https://docs.pieces.app/products/cli/commands#commit"
    CLI_ONBOARDING_DOCS = "https://docs.pieces.app/products/cli/commands#onboarding"
    CLI_FEEDBACK_DOCS = "https://docs.pieces.app/products/cli/commands#feedback"
    CLI_CONTRIBUTE_DOCS = "https://docs.pieces.app/products/cli/commands#contribute"
    CLI_INSTALL_DOCS = "https://docs.pieces.app/products/cli/commands#install"
    CLI_OPEN_DOCS = "https://docs.pieces.app/products/cli/commands#open"
    CLI_HELP_DOCS = "https://docs.pieces.app/products/cli/troubleshooting"
    CLI_COMPLETION_DOCS = ""

    def open(self):
        self.open_website(self.value)

    @staticmethod
    def open_website(url: str):
        from pieces.settings import Settings

        if hasattr(Settings.pieces_client, "user_api"):
            user_profile = Settings.pieces_client.user_api.user_snapshot().user
            if (not Settings.pieces_client.is_pieces_running()) or (
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
            Settings.logger.critical(f"Failed to open a url {e}")
            Settings.logger.print(f"Failed to open {url}")
