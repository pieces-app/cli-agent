import argparse
import asyncio
from typing import Union
from pieces.base_command import BaseCommand, CommandGroup
from pieces.headless.models.base import CommandResult
from pieces.mcp import (
    handle_gateway,
    handle_list,
    handle_mcp,
    handle_mcp_docs,
    handle_repair,
    handle_status,
    handle_list_headless,
)
from pieces.config.schemas.mcp import mcp_integrations
from pieces.settings import Settings
from pieces.urls import URLs


class MCPSetupCommand(BaseCommand):
    """Subcommand to set up MCP integrations."""

    _is_command_group = True
    support_headless = True

    def get_name(self) -> str:
        return "setup"

    def get_help(self) -> str:
        return "Set up an integration"

    def get_description(self) -> str:
        return "Set up MCP server for various IDE integrations"

    def get_examples(self) -> list[str]:
        return [
            "pieces mcp setup vscode",
            "pieces mcp setup cursor --globally",
            "pieces mcp setup claude --stdio",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_SETUP_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "integration",
            type=str,
            choices=mcp_integrations + ["raycast", "wrap"],
            help="The integration to set up",
            default=None,
            nargs="?",
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
            nargs="?",
            const=True,
            help="For VS Code or Cursor to set the Local MCP",
        )
        parser.add_argument(
            "--stdio",
            dest="stdio",
            action="store_true",
            help="Use the stdio MCP instead of sse",
        )

    def execute(self, **kwargs) -> CommandResult:
        """Execute the MCP setup command."""
        result = handle_mcp(**kwargs)
        return CommandResult(
            0,
            result,
        )


class MCPListCommand(BaseCommand):
    """Subcommand to list MCP integrations."""

    _is_command_group = True
    support_headless = True

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

    def execute(self, **kwargs) -> Union[int, CommandResult]:
        if not Settings.headless_mode:
            handle_list(**kwargs)
            return 0
        else:
            return CommandResult(0, handle_list_headless(**kwargs))


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
            "pieces mcp docs --integration vscode",
            "pieces mcp docs --integration cursor --open",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_DOCS_COMMAND.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--integration",
            "-i",
            dest="ide",
            type=str,
            choices=mcp_integrations + ["all", "current", "raycast", "wrap"],
            default="all",
            help="The integration to print its documentation",
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
        """Execute the start command."""
        try:
            # Check if event loop is already running
            try:
                loop = asyncio.get_running_loop()
                Settings.logger.error(
                    "Cannot start MCP server: Event loop already running"
                )
                return 1
            except RuntimeError:
                # No event loop running, safe to proceed
                pass

            asyncio.run(handle_gateway())
            return 0
        except KeyboardInterrupt:
            return 0
        except Exception as e:
            Settings.logger.error(f"Failed to start MCP server: {e}")
            Settings.logger.console_error.print("Failed to start MCP server")
            return 1


class MCPRepairCommand(BaseCommand):
    """Subcommand to repair MCP configurations."""

    _is_command_group = True
    support_headless = True

    def get_name(self) -> str:
        return "repair"

    def get_help(self) -> str:
        return "Repair an MCP config settings"

    def get_description(self) -> str:
        return "Repair MCP configuration settings for specific IDEs"

    def get_examples(self) -> list[str]:
        return [
            "pieces mcp repair",
            "pieces mcp repair --integration vscode",
            "pieces mcp repair --integration all",
        ]

    def get_docs(self) -> str:
        return URLs.CLI_MCP_REPAIR_DOCS.value

    def add_arguments(self, parser: argparse.ArgumentParser):
        parser.add_argument(
            "--integration",
            "-i",
            dest="ide",
            type=str,
            choices=mcp_integrations + ["all"],
            default="all",
            help="The integration to repair",
        )

    def execute(self, **kwargs) -> Union[int, CommandResult]:
        if not Settings.headless_mode:
            handle_repair(**kwargs)
            return 0
        else:
            result = handle_repair(**kwargs)
            return CommandResult(0, result)


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
            "pieces mcp setup vscode",
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
