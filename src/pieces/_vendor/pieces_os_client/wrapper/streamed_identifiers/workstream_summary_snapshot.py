import threading
from typing import TYPE_CHECKING, Dict


from ._streamed_identifiers import StreamedIdentifiersCache

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.workstream_summary import (
        WorkstreamSummary,
    )


class WorkstreamSummarySnapshot(StreamedIdentifiersCache):
    """
    A class to represent a snapshot of all the cached WorkstreamSummaries.

    Class attributes:
    identifiers_snapshot (dict): A dictionary where the keys are UUIDs (unique identifiers) and the values are Conversation objects.
    """

    _initialized: threading.Event
    identifiers_snapshot: Dict[
        str, "WorkstreamSummary"
    ] = {}  # Map id:return from the _api_call

    @staticmethod
    def _name() -> str:
        return "workstream_summary"

    @classmethod
    def _api_call(cls, id):
        return cls.pieces_client.workstream_summary_api.workstream_summaries_specific_workstream_summary_snapshot(
            id
        )

    @staticmethod
    def _sort_first_shot():
        pass
