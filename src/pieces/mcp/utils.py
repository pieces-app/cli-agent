from typing import TYPE_CHECKING, List
from ..settings import Settings

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.model_context_protocol_schema_version import (
        ModelContextProtocolSchemaVersion,
    )

_latest_urls = []  # cache the urls instead of sending to the api


def get_mcp_model_urls() -> List["ModelContextProtocolSchemaVersion"]:
    global _latest_urls
    if not _latest_urls:
        res = Settings.pieces_client.model_context_protocol_api.model_context_protocol_schema_versions()
        _latest_urls = res.iterable
    return _latest_urls


def get_mcp_latest_url():
    return get_mcp_model_urls()[0].entry_endpoint


def get_mcp_urls():
    return [mcp.entry_endpoint for mcp in get_mcp_model_urls()]
