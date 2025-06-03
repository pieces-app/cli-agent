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

    def open(self):
        self.open_website(self.value)

    @staticmethod
    def open_website(url: str):
        from pieces.settings import Settings

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
