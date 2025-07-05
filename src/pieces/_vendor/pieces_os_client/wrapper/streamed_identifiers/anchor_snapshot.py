import threading
from typing import TYPE_CHECKING, Dict

from ._streamed_identifiers import StreamedIdentifiersCache

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.anchor import Anchor


class AnchorSnapshot(StreamedIdentifiersCache):
    """
    A class to represent a snapshot of all the cached Assets.
    """

    _initialized: threading.Event
    identifiers_snapshot: Dict[str, "Anchor"] = {}  # Map id:return from the _api_call

    @staticmethod
    def _name() -> str:
        return "anchor"

    @classmethod
    def _api_call(cls, id):
        anchor = cls.pieces_client.anchor_api.anchor_specific_anchor_snapshot(id)
        return anchor

    @staticmethod
    def _sort_first_shot():
        pass
