import threading
from typing import TYPE_CHECKING, Dict

from ._streamed_identifiers import StreamedIdentifiersCache


if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.range import Range


class RangeSnapshot(StreamedIdentifiersCache):
    """
    A class to represent a snapshot of all the cached Conversations.

    Class attributes:
    identifiers_snapshot (dict): A dictionary where the keys are UUIDs (unique identifiers) and the values are Conversation objects.
    """

    _initialized: threading.Event
    identifiers_snapshot: Dict[str, "Range"] = {}  # Map id:return from the _api_call

    @staticmethod
    def _name() -> str:
        return "range"

    @classmethod
    def _sort_first_shot(cls):
        # Sort the dictionary by the "created" timestamp
        sorted_ranges = sorted(
            cls.identifiers_snapshot.values(),
            key=lambda x: x.created.value,
            reverse=True,
        )
        cls.identifiers_snapshot = {range.id: range for range in sorted_ranges}

    @classmethod
    def _api_call(cls, id):
        range = cls.pieces_client.range_api.ranges_specific_range_snapshot(id)
        return range
