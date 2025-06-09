import threading
from typing import TYPE_CHECKING, Dict

from ._streamed_identifiers import StreamedIdentifiersCache

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.asset import Asset


class AssetSnapshot(StreamedIdentifiersCache):
    """
    A class to represent a snapshot of all the cached Assets.
    """

    _initialized: threading.Event
    identifiers_snapshot: Dict[str, "Asset"] = {}  # Map id:return from the _api_call

    @staticmethod
    def _name() -> str:
        return "asset"

    @classmethod
    def _api_call(cls, id):
        asset = cls.pieces_client.asset_api.asset_snapshot(id)
        return asset

    @staticmethod
    def _sort_first_shot():
        pass
