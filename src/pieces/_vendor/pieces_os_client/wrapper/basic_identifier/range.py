import datetime
from typing import TYPE_CHECKING, Optional
from .basic import Basic
from ..streamed_identifiers.range_snapshot import RangeSnapshot

if TYPE_CHECKING:
    from .chat import BasicChat
    from pieces._vendor.pieces_os_client.models.range import Range


class BasicRange(Basic):
    def __init__(self, id: str) -> None:
        """
        Initializes a BasicRange instance.

        Args:
        - id (str): The ID of the range.
        """
        self.pieces_client = RangeSnapshot.pieces_client
        super().__init__(id)

    @property
    def range(self) -> "Range":
        range = RangeSnapshot.identifiers_snapshot.get(self._id)
        range = RangeSnapshot.update_identifier(self._id)
        if not range:
            raise ValueError("Range not found")
        return range

    @property
    def id(self):
        return self.range.id

    @classmethod
    def get_latest(cls) -> "BasicRange":
        """Returns the latest range"""
        range = list(RangeSnapshot.identifiers_snapshot.keys())
        if range:
            range = range[-1]
        else:
            return BasicRange.create()
        return BasicRange(range)

    def associate_chat(self, chat: "BasicChat"):
        """
        Associates a chat to a range.

        Args:
        - chat (BasicChat): The BasicChat object to associate.
        """
        RangeSnapshot.pieces_client.range_api.range_associate_conversation_grounding_temporal_range_workstreams(
            self.id, chat.id
        )

    def disassociate_chat(self, chat: "BasicChat"):
        """
        Disassociates a chat from a range.

        Args:
        - chat (BasicChat): The BasicChat object to disassociate.
        """
        RangeSnapshot.pieces_client.range_api.range_disassociate_conversation_grounding_temporal_range_workstreams(
            self.id, chat.id
        )

    @staticmethod
    def create(
        from_: Optional[datetime.datetime] = None,
        to: Optional[datetime.datetime] = datetime.datetime.now(),
    ) -> "BasicRange":
        """
        Creates a new range based on a Range.

        Args:
        - from_ (datetime.datetime): The start date of the range. Optional.
        - to (datetime.datetime): The end date of the range. Optional.

        Returns:
        - BasicRange: The created BasicRange instance.
        """
        from pieces._vendor.pieces_os_client.models.seeded_range import SeededRange
        from pieces._vendor.pieces_os_client.models.grouped_timestamp import GroupedTimestamp
        if not from_:
            from_ = datetime.datetime.now() - datetime.timedelta(minutes=15)

        r = RangeSnapshot.pieces_client.ranges_api.ranges_create_new_range(
            SeededRange(
                var_from=GroupedTimestamp(value=from_) if from_ else None,
                to=GroupedTimestamp(value=to) if to else None,
            )
        )
        RangeSnapshot.identifiers_snapshot[r.id] = r
        return BasicRange(r.id)
