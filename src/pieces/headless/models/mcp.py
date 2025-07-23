"""
MCP command response models for headless mode.
"""

from typing import List, Literal, Optional
from .base import SuccessResponse


def create_mcp_setup_success(
    integration_name: str,
    configuration_path: Optional[str],
    instructions: str,
    setup_type: Literal["stdio", "sse"] = "stdio",
    location_type: Literal["local", "global"] = "global",
) -> SuccessResponse:
    """Create a successful MCP setup response."""
    setup_data = {
        "integration_name": integration_name,
        "setup_type": setup_type,
        "instructions": instructions,
        "configuration_path": configuration_path,
        "location_type": location_type,
    }

    return SuccessResponse(command="mcp setup", data=setup_data)


class MCPListResponse:
    def __init__(
        self,
        integration_name: str,
        status: Literal["activated", "available_to_setup", "needs_repair", "not_found"],
    ):
        self.integration_name = integration_name
        self.status = status

    def to_dict(self):
        return {
            "integration_name": self.integration_name,
            "status": self.status,
        }


def create_mcp_list_success(
    integrations: List[MCPListResponse],
):
    return SuccessResponse(
        command="mcp list",
        data={"integrations": [integration.to_dict() for integration in integrations]},
    )


class MCPRepairResult:
    def __init__(
        self,
        integration_name: str,
        status: Literal["repaired", "healthy", "failed"],
        configuration_path: Optional[str] = None,
    ):
        self.integration_name = integration_name
        self.status = status
        self.configuration_path = configuration_path

    def to_dict(self):
        result = {
            "integration_name": self.integration_name,
            "status": self.status,
        }
        if self.configuration_path:
            result["configuration_path"] = self.configuration_path
        return result


def create_mcp_repair_success(repair_results: List[MCPRepairResult]) -> SuccessResponse:
    """Create a successful MCP repair response.

    Args:
        repair_results: List of repair results for each integration

    Returns:
        SuccessResponse with repair results data
    """
    return SuccessResponse(
        command="mcp repair",
        data={
            "repairs": [result.to_dict() for result in repair_results],
            "summary": {
                "total": len(repair_results),
                "repaired": len([r for r in repair_results if r.status == "repaired"]),
                "healthy": len([r for r in repair_results if r.status == "healthy"]),
                "failed": len([r for r in repair_results if r.status == "failed"]),
            },
        },
    )
