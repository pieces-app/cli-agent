import argparse
import asyncio
from pieces.base_command import BaseCommand, CommandGroup
from pieces.urls import URLs
from pieces.mcp import (
    handle_mcp,
    handle_list,
    handle_mcp_docs,
    handle_repair,
    handle_status,
    handle_gateway,
)


class MCPSetupCommand(BaseCommand):
    """Subcommand to set up MCP integrations."""

    _is_command_group = True

    def get_name(self) -> str:
        return "setup"

    def get_help(self) -> str:
        return "Sets up a integration"

    def get_description(self) -> str:
        return "Set up MCP server for various IDE integrations"

    def get_examples(self) -> list[str]:
        return [
            "pieces mcp setup --vscode",
            "pieces mcp setup --cursor --globally",
            "pieces mcp setup --claude --stdio",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_SETUP_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--vscode",
            dest="vscode",
            action="store_true",
            help="Set up the MCP for VS Code",
        )
        parser.add_argument(
            "--globally",
            dest="global",
            action="store_true",
            help="For VS Code or Cursor to set the Global MCP",
        )
        parser.add_argument(
            "--specific-workspace",
            dest="local",
            action="store_true",
            help="For VS Code or Cursor to set the Local MCP",
        )
        parser.add_argument(
            "--cursor",
            dest="cursor",
            action="store_true",
            help="Set up the MCP for Cursor",
        )
        parser.add_argument(
            "--goose",
            dest="goose",
            action="store_true",
            help="Set up the MCP for Goose",
        )
        parser.add_argument(
            "--claude",
            dest="claude",
            action="store_true",
            help="Set up the MCP for Claude Desktop",
        )
        parser.add_argument(
            "--stdio",
            dest="stdio",
            action="store_true",
            help="Use the stdio MCP instead of sse",
        )

    def execute(self, **kwargs) -> int:
        handle_mcp(**kwargs)
        return 0


class MCPListCommand(BaseCommand):
    """Subcommand to list MCP integrations."""

    _is_command_group = True

    def get_name(self) -> str:
        return "list"

    def get_help(self) -> str:
        return "List all MCP integrations"

    def get_description(self) -> str:
        return "Display registered and available MCP integrations"

    def get_examples(self) -> list[str]:
        return [
            "pieces mcp list",
            "pieces mcp list --already-registered",
            "pieces mcp list --available-for-setup",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_LIST_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--already-registered",
            dest="already_registered",
            action="store_true",
            help="Display the list of the registered MCPs",
        )
        parser.add_argument(
            "--available-for-setup",
            dest="available_for_setup",
            action="store_true",
            help="Display the list of the ready to be registered MCPs",
        )

    def execute(self, **kwargs) -> int:
        handle_list(**kwargs)
        return 0


class MCPDocsCommand(BaseCommand):
    """Subcommand to display MCP documentation."""

    _is_command_group = True

    def get_name(self) -> str:
        return "docs"

    def get_help(self) -> str:
        return "Print the documentations for an integration"

    def get_description(self) -> str:
        return "Display or open documentation for MCP integrations"

    def get_examples(self) -> list[str]:
        return [
            "pieces mcp docs",
            "pieces mcp docs --ide vscode",
            "pieces mcp docs --ide cursor --open",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_DOCS_COMMAND.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--ide",
            dest="ide",
            type=str,
            choices=["vscode", "cursor", "goose", "claude", "current", "all"],
            default="all",
            help="The IDE to print its documentation",
        )
        parser.add_argument(
            "--open",
            "-o",
            dest="open",
            action="store_true",
            help="Open the queried docs in the browser",
        )

    def execute(self, **kwargs) -> int:
        handle_mcp_docs(**kwargs)
        return 0


class MCPStartCommand(BaseCommand):
    """Subcommand to start MCP server."""

    _is_command_group = True

    def get_name(self) -> str:
        return "start"

    def get_help(self) -> str:
        return "Start the stdio MCP server"

    def get_description(self) -> str:
        return "Start the MCP server in stdio mode"

    def get_examples(self) -> list[str]:
        return ["pieces mcp start"]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_START_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        asyncio.run(handle_gateway())
        return 0


class MCPRepairCommand(BaseCommand):
    """Subcommand to repair MCP configurations."""

    _is_command_group = True

    def get_name(self) -> str:
        return "repair"

    def get_help(self) -> str:
        return "Repair an MCP config settings"

    def get_description(self) -> str:
        return "Repair MCP configuration settings for specific IDEs"

    def get_examples(self) -> list[str]:
        return [
            "pieces mcp repair",
            "pieces mcp repair --ide vscode",
            "pieces mcp repair --ide all",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_REPAIR_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--ide",
            dest="ide",
            type=str,
            choices=["vscode", "cursor", "goose", "claude", "all"],
            default="all",
            help="The IDE to repair",
        )

    def execute(self, **kwargs) -> int:
        handle_repair(**kwargs)
        return 0


class MCPStatusCommand(BaseCommand):
    """Subcommand to show MCP status."""

    _is_command_group = True

    def get_name(self) -> str:
        return "status"

    def get_help(self) -> str:
        return "Show the Status of the LTM and the MCPs"

    def get_description(self) -> str:
        return "Display the current status of LTM and MCP integrations"

    def get_examples(self) -> list[str]:
        return ["pieces mcp status"]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_STATUS_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        pass

    def execute(self, **kwargs) -> int:
        handle_status(**kwargs)
        return 0


class MCPCommandGroup(CommandGroup):
    """MCP command group for managing integrations."""

    def get_name(self) -> str:
        return "mcp"

    def get_help(self) -> str:
        return "setup the MCP server for an integration"

    def get_description(self) -> str:
        return "Manage Model Context Protocol (MCP) integrations for various IDEs and tools including VS Code, Cursor, Claude Desktop, and Goose"

    def get_examples(self) -> list[str]:
        return [
            "pieces mcp",
            "pieces mcp setup --vscode",
            "pieces mcp list",
            "pieces mcp status",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_DOCS.value

    def _register_subcommands(self):
        """Register all MCP subcommands."""
        self.add_subcommand(MCPSetupCommand())
        self.add_subcommand(MCPListCommand())
        self.add_subcommand(MCPDocsCommand())
        self.add_subcommand(MCPStartCommand())
        self.add_subcommand(MCPRepairCommand())
        self.add_subcommand(MCPStatusCommand())

    def execute(self, **kwargs) -> int:
        """When no subcommand is provided, show help."""
        self.parser.print_help()
        return 0
