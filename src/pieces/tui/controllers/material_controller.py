"""Controller for handling material-related events."""
# We gonna add the saved materials view at some point, for now we don't need it
# from typing import List, TYPE_CHECKING
# from pieces.settings import Settings
# from .base_controller import BaseController, EventType
#
# if TYPE_CHECKING:
#     from pieces._vendor.pieces_os_client.models.asset import Asset
#     from pieces._vendor.pieces_os_client.wrapper.basic_identifier.asset import (
#         BasicAsset,
#     )
#
#
# class MaterialController(BaseController):
#     """Handles material-related events from the backend."""
#
#     def __init__(self):
#         """Initialize the material controller."""
#         super().__init__()
#         self._asset_ws = None
#         self._context_materials: List["BasicAsset"] = []
#
#     def initialize(self):
#         """Set up WebSocket listeners for material events."""
#         from pieces._vendor.pieces_os_client.wrapper.websockets.assets_identifiers_ws import (
#             AssetsIdentifiersWS,
#         )
#
#         if self._initialized:
#             return
#
#         try:
#             # Get the WebSocket instance
#
#             # Create WebSocket with callbacks
#             self._asset_ws = AssetsIdentifiersWS.get_instance() or AssetsIdentifiersWS(
#                 pieces_client=Settings.pieces_client,
#                 on_asset_update=self._on_asset_update,
#                 on_asset_remove=self._on_asset_remove,
#             )
#
#             # Start the WebSocket
#             self._asset_ws.start()
#
#             self._initialized = True
#             Settings.logger.info("MaterialController initialized")
#
#         except Exception as e:
#             Settings.logger.error(f"Failed to initialize MaterialController: {e}")
#
#     def cleanup(self):
#         """Stop listening to material events."""
#         try:
#             if self._asset_ws:
#                 self._asset_ws.close()
#         except Exception as e:
#             Settings.logger.error(f"Error closing asset WebSocket: {e}")
#         finally:
#             self._asset_ws = None
#
#         # Clear context materials
#         self._context_materials.clear()
#
#         # Clear all event listeners
#         self._safe_cleanup()
#
#     def _on_asset_update(self, asset: "Asset"):
#         """Handle material update from WebSocket."""
#         try:
#             # Determine if this is a new material or an update
#             is_new = asset.created.value == asset.updated.value
#
#             if is_new:
#                 self.emit(EventType.MATERIAL_CREATED, asset)
#             else:
#                 self.emit(EventType.MATERIAL_UPDATED, asset)
#
#         except Exception as e:
#             Settings.logger.error(f"Error handling material update: {e}")
#
#     def _on_asset_remove(self, asset: "Asset"):
#         """Handle material removal from WebSocket."""
#         try:
#             self.emit(EventType.MATERIAL_DELETED, asset)
#
#             # Remove from context if present
#             self._remove_from_context(asset.id)
#
#         except Exception as e:
#             Settings.logger.error(f"Error handling material removal: {e}")
#
#     def add_to_context(self, material: "BasicAsset"):
#         """
#         Add a material to the chat context.
#
#         Args:
#             material: The material to add to context
#         """
#         try:
#             # Check if already in context
#             for existing in self._context_materials:
#                 if existing.id == material.id:
#                     return
#
#             self._context_materials.append(material)
#             self.emit(
#                 EventType.CONTEXT_ADDED,
#                 {
#                     "type": "material",
#                     "item": material,
#                     "total_count": len(self._context_materials),
#                 },
#             )
#
#         except Exception as e:
#             Settings.logger.error(f"Error adding material to context: {e}")
#
#     def remove_from_context(self, material_id: str):
#         """
#         Remove a material from the chat context.
#
#         Args:
#             material_id: ID of the material to remove
#         """
#         self._remove_from_context(material_id)
#
#     def _remove_from_context(self, material_id: str):
#         """Internal method to remove material from context."""
#         try:
#             removed = None
#             for i, material in enumerate(self._context_materials):
#                 if material.id == material_id:
#                     removed = self._context_materials.pop(i)
#                     break
#
#             if removed:
#                 self.emit(
#                     EventType.CONTEXT_REMOVED,
#                     {
#                         "type": "material",
#                         "item": removed,
#                         "total_count": len(self._context_materials),
#                     },
#                 )
#
#         except Exception as e:
#             Settings.logger.error(f"Error removing material from context: {e}")
#
#     def clear_context(self):
#         """Clear all materials from the chat context."""
#         try:
#             count = len(self._context_materials)
#             self._context_materials.clear()
#
#             if count > 0:
#                 self.emit(
#                     EventType.CONTEXT_CLEARED,
#                     {"type": "materials", "previous_count": count},
#                 )
#
#         except Exception as e:
#             Settings.logger.error(f"Error clearing material context: {e}")
#
#     def get_context_materials(self) -> List["BasicAsset"]:
#         """Get all materials currently in context."""
#         return self._context_materials.copy()
#
#     def search_materials(self, query: str):
#         """
#         Search for materials.
#
#         Args:
#             query: Search query
#         """
#         try:
#             # Perform search
#             results = BasicAsset.search(
#                 query=query,
#             )
#
#             # Emit results
#             self.emit(EventType.MATERIALS_SEARCH_COMPLETED, results or [])
#
#             return results
#
#         except Exception as e:
#             Settings.logger.error(f"Error searching materials: {e}")
#             return []
