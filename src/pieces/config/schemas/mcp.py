"""
MCP (Model Context Protocol) configuration schema.
"""

from typing import Dict, Literal, get_args, List
from pydantic import Field, field_validator, create_model
from pieces.config.utils import validate_semver


mcp_types = Literal["sse", "stdio"]

IntegrationDict = Dict[str, mcp_types]

mcp_integration_types = Literal[
    "vscode",
    "goose",
    "cursor",
    "claude",
    "windsurf",
    "zed",
    "shortwave",
    "claude_code",
    "kiro",
]

mcp_integrations: List[mcp_integration_types] = list(get_args(mcp_integration_types))


# Dynamic schema creation
def _create_mcp_config_schema():
    """Create MCP config schema with dynamic integration fields."""

    # Base fields
    fields = {
        "schema_version": (
            str,
            Field(default="0.0.1", description="Configuration schema version"),
        ),
    }

    # Add dynamic integration fields
    for integration in mcp_integrations:
        fields[integration] = (  # type: ignore[arg-type]
            Dict[str, mcp_types],
            Field(
                default_factory=dict,
                description=f"{integration.title()} integration projects",
            ),
        )

    # Create the model
    MCPConfigSchema = create_model(  # type: ignore[call-arg]
        "MCPConfigSchema",
        **fields,  # type: ignore[arg-type]
        __module__=__name__,
    )

    # Add validators
    @field_validator("schema_version", mode="before")
    @classmethod
    def validate_schema(cls, v):
        return validate_semver(v)

    # Add the validator to the class
    MCPConfigSchema.validate_schema = validate_schema

    # Set config
    MCPConfigSchema.model_config = {"extra": "forbid"}

    # Add docstring
    MCPConfigSchema.__doc__ = (
        "Schema for MCP configuration - dynamically includes all integration types."
    )

    return MCPConfigSchema


# Create the dynamic schema
MCPConfigSchema = _create_mcp_config_schema()
