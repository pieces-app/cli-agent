"""
Shared utilities for MCP-related unit tests.

This module centralizes common mocks, patch helpers, and a base
``unittest.TestCase`` that other test modules can inherit from to prevent
repetition (DRY principle).
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, cast, List
from unittest import TestCase
from unittest.mock import Mock, patch

# Third-party imports (Pieces)
from pieces.config.managers.mcp import MCPManager
from pieces.mcp.integration import MCPProperties  # noqa: E402 (after sys path)

__all__ = [
    "MockPiecesClient",
    "default_mcp_properties",
    "patch_mcp_schema",
    "MCPTestBase",
]


class MockPiecesClient(Mock):
    """A lightweight stub for :class:`pieces.PiecesClient` used in tests."""

    def __init__(self, *args, **kwargs):  # noqa: D401, D403 – allow flexible kwargs
        super().__init__(*args, **kwargs)

        # Inner API client stub (used by generated swagger client)
        self.api_client = Mock()

        # Import lazily to avoid heavy dependency cost when tests unrelated to
        # MCP utilities run.
        from pieces._vendor.pieces_os_client.api.workstream_pattern_engine_api import (  # noqa: E501
            WorkstreamPatternEngineApi,
        )
        from pieces._vendor.pieces_os_client.api.model_context_protocol_api import (
            ModelContextProtocolApi,
        )

        self._work_stream_pattern_engine_api = WorkstreamPatternEngineApi(
            self.api_client
        )
        self._model_context_protocol_api = ModelContextProtocolApi(self.api_client)

        # Copilot / LTM stubs
        self.copilot = Mock()
        self.copilot.context = Mock()
        self.copilot.context.ltm = Mock()
        self.copilot.context.ltm.is_enabled = False
        self.copilot.context.ltm.check_perms = Mock(return_value=[])
        self.copilot.context.ltm.enable = Mock()
        self.copilot.context.ltm.ltm_status = None

        # Misc network-level attributes expected by some integrations
        self._port = "39300"
        self.host = "http://127.0.0.1:39300"
        self.is_pieces_running = Mock(return_value=True)
        self.init_host = Mock()

    # Properties expected by upstream code ---------------------------------

    @property
    def work_stream_pattern_engine_api(self):  # noqa: D401
        return self._work_stream_pattern_engine_api

    @property
    def model_context_protocol_api(self):  # noqa: D401
        return self._model_context_protocol_api


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def default_mcp_properties() -> MCPProperties:
    """Return a *default* :class:`MCPProperties` instance used across tests."""

    return MCPProperties(
        stdio_property={"type": "stdio"},
        stdio_path=["mcp", "servers", "Pieces"],
        sse_property={"type": "sse"},
        sse_path=["mcp", "servers", "Pieces"],
        url_property_name="url",
        command_property_name="command",
        args_property_name="args",
    )


def patch_mcp_schema(integration_id: str = "test_integration") -> None:
    """Dynamically add *integration_id* to the MCP schema for tests.

    The actual production schema does **not** contain a ``test_integration``
    field.  To prevent Pydantic validation errors when tests attempt to write
    to this attribute via :class:`pieces.config.managers.mcp.MCPManager`, we
    monkey-patch the schema at runtime:

    1. Append the ID to the global ``mcp_integrations`` list.
    2. Re-generate ``MCPConfigSchema`` so it contains the new field.
    3. Loosen the model config to ``extra = \"allow\"`` so any other ad-hoc
       test integrations remain valid without further changes.
    """

    import pieces.config.schemas.mcp as mcp_schema

    if integration_id not in mcp_schema.mcp_integrations:
        # Dynamically register the new integration identifier so that downstream
        # helpers (e.g., :pyclass:`MCPManager`) iterate over it.
        mcp_schema.mcp_integrations.append(cast(Any, integration_id))

        # Re-create the Pydantic model so it now includes the new field.
        mcp_schema.MCPConfigSchema = mcp_schema._create_mcp_config_schema()  # type: ignore[attr-defined]  # noqa: E501

        # Allow extra attributes to avoid future friction when tests need yet
        # another synthetic integration ID.
        mcp_schema.MCPConfigSchema.model_config["extra"] = "allow"  # type: ignore[index]

        # Update already-imported references (e.g., in MCPManager) so they use
        # the *new* schema instance.
        import pieces.config.managers.mcp as mcp_manager_module

        mcp_manager_module.MCPConfigSchema = mcp_schema.MCPConfigSchema


# ---------------------------------------------------------------------------
# Base TestCase
# ---------------------------------------------------------------------------


class MCPTestBase(TestCase):
    """Common boilerplate for MCP-oriented unit tests."""

    integration_id: str = "test_integration"

    # Patchers – stored as *class* attributes so tearDownClass can access them
    settings_patcher: Any  # noqa: ANN401 – late binding
    integration_settings_patcher: Any
    mcp_urls_patcher: Any
    mcp_latest_url_patcher: Any
    tmp_dir_context: tempfile.TemporaryDirectory[str]

    @classmethod
    def setUpClass(cls) -> None:  # noqa: D401 – overrides TestCase hook
        super().setUpClass()

        # 1. Ensure schema can handle the synthetic integration ID -------------
        patch_mcp_schema(cls.integration_id)

        # 2. Temporary directory for config file --------------------------------
        cls.tmp_dir_context = tempfile.TemporaryDirectory()
        tmp_config_path = Path(cls.tmp_dir_context.name) / "mcp.json"

        # 3. Patch Settings in the *core* module --------------------------------
        cls.settings_patcher = patch("pieces.settings.Settings")
        cls.mock_settings = cls.settings_patcher.start()

        # Provide a real MCPManager backed by the temporary file
        cls.mock_settings.mcp_config = MCPManager(tmp_config_path)

        # ------------------------------------------------------------------
        # Use the *real* logger implementation so tests can exercise its
        #   info / debug / error paths instead of silently swallowing logs.
        #   We override only interactive pieces (confirm / prompt) so that
        #   tests remain non-blocking.
        # ------------------------------------------------------------------
        from pieces.logger import Logger  # local import to avoid early side-effects

        real_logger = Logger(debug_mode=False)

        # Stubs that bypass interactive prompts but keep the call signature
        real_logger.confirm = lambda *_, **__: True  # type: ignore[assignment]
        real_logger.prompt = lambda *_, **__: ""  # type: ignore[assignment]

        cls.mock_settings.logger = real_logger

        # 4. Make sure *integration.py* resolves to the same mocked Settings ----
        cls.integration_settings_patcher = patch(
            "pieces.mcp.integration.Settings", cls.mock_settings
        )
        cls.integration_settings_patcher.start()

        cls.mcp_get_urls_patcher = patch(
            "pieces.mcp.utils.get_mcp_model_urls",
            return_value=[Mock(entry_endpoint="pieces_url")],
        )
        cls.mcp_get_urls_patcher.start()
        cls.integration_get_urls_patcher = patch(
            "pieces.mcp.integration.get_mcp_urls", return_value=["pieces_url"]
        )
        cls.integration_get_urls_patcher.start()

        # Ensure original utility get_mcp_urls is patched as well (even though
        # integration.py now has its own reference) so any *new* imports in
        # runtime code paths stay stubbed.
        cls.mcp_urls_patcher = patch(
            "pieces.mcp.utils.get_mcp_urls", return_value=["pieces_url"]
        )
        cls.mcp_urls_patcher.start()

        cls.mcp_latest_url_patcher = patch(
            "pieces.mcp.integration.get_mcp_latest_url", return_value="pieces_url"
        )
        cls.mcp_latest_url_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:  # noqa: D401 – overrides TestCase hook
        super().tearDownClass()

        # Stop patchers in *reverse* order of creation
        cls.mcp_latest_url_patcher.stop()
        cls.integration_get_urls_patcher.stop()
        cls.mcp_get_urls_patcher.stop()
        cls.mcp_urls_patcher.stop()
        cls.integration_settings_patcher.stop()
        cls.settings_patcher.stop()

        # Clean up temp directory
        cls.tmp_dir_context.cleanup()

    # ------------------------------------------------------------------
    # Convenience helpers for subclasses
    # ------------------------------------------------------------------

    def create_mock_client(self) -> MockPiecesClient:
        """Return a fresh :class:`MockPiecesClient` instance."""
        return MockPiecesClient()

    def get_mcp_properties(self) -> MCPProperties:
        """Return a default :class:`MCPProperties` instance."""
        return default_mcp_properties()

