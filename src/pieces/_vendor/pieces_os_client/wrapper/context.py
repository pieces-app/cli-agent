from typing import TYPE_CHECKING, List, Callable, Optional, SupportsIndex
import os

from .long_term_memory import LongTermMemory

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.temporal_range_grounding import TemporalRangeGrounding
    from . import PiecesClient
    from .copilot import Copilot
    from .basic_identifier.chat import BasicChat
    from .basic_identifier.message import BasicMessage
    from .basic_identifier.asset import BasicAsset


class ValidatedContextList(List):
    """
    This is a list that notifies the callables if any item is added or removed from it.
    """

    def __init__(self, *args, on_add: Callable, on_remove: Callable):
        self.on_add = on_add
        self.on_remove = on_remove
        super().__init__()
        for arg in args:
            self.append(arg)

    def append(self, value):
        self.on_add(value)
        super().append(value)

    def extend(self, iterable):
        for value in iterable:
            self.append(value)

    def insert(self, index, value):
        self.on_add(value)
        super().insert(index, value)

    def remove(self, value):
        index = self.index(value)
        self.on_remove(index)
        super().remove(value)

    def __setitem__(self, index, value):
        self.on_remove(index)
        self.on_add(value)
        super().__setitem__(index, value)

    def __iadd__(self, other):
        for value in other:
            self.append(value)
        return self

    def __add__(self, other):
        new_list = ValidatedContextList(
            self, on_add=self.on_add, on_remove=self.on_remove
        )
        for value in other:
            new_list.append(value)
        return new_list

    def pop(self, index: SupportsIndex = -1):
        value = super().pop(index)
        self.on_remove(index)
        return value

    def clear(self, **kwargs):
        if kwargs.get("_notifiy", True):
            for item in range(len(self)):
                self.on_remove(item)

        super().clear()


class Context:
    def __init__(
        self,
        pieces_client: "PiecesClient",
        copilot: "Copilot",
        paths: Optional[List[str]] = None,
        raw_assets: Optional[List[str]] = None,
        assets: Optional[List["BasicAsset"]] = None,
        messages: Optional[List["BasicMessage"]] = None,
    ):
        from pieces._vendor.pieces_os_client.models.anchors import Anchors
        from pieces._vendor.pieces_os_client.models.assets import Assets
        from pieces._vendor.pieces_os_client.models.seeds import Seeds
        from pieces._vendor.pieces_os_client.models.flattened_conversation_messages import (
            FlattenedConversationMessages,
        )

        self.pieces_client = pieces_client
        self.raw_assets: List[str] = (
            ValidatedContextList(
                raw_assets, on_add=self._add_raw_asset, on_remove=self._remove_raw_asset
            )
            if raw_assets is not None
            else ValidatedContextList(
                on_add=self._add_raw_asset, on_remove=self._remove_raw_asset
            )
        )
        self.paths: List[str] = (
            ValidatedContextList(
                paths, on_add=self._add_path, on_remove=self._remove_path
            )
            if paths is not None
            else ValidatedContextList(
                on_add=self._add_path, on_remove=self._remove_path
            )
        )
        self.assets: List["BasicAsset"] = (
            ValidatedContextList(
                assets, on_add=self._add_asset, on_remove=self._remove_asset
            )
            if assets is not None
            else ValidatedContextList(
                on_add=self._add_asset, on_remove=self._remove_asset
            )
        )
        self.messages: List["BasicMessage"] = (
            ValidatedContextList(
                messages, on_add=self._add_message, on_remove=self._remove_message
            )
            if messages is not None
            else ValidatedContextList(
                on_add=self._add_message, on_remove=self._remove_message
            )
        )
        self.copilot = copilot
        self.ltm = LongTermMemory(self)

        ## Internal stuff
        self._assets: Assets = Assets(iterable=[])
        self._raw_assets: Seeds = Seeds(iterable=[])
        self._messages: FlattenedConversationMessages = FlattenedConversationMessages(
            iterable=[]
        )
        self._paths: Anchors = Anchors(iterable=[])

    def clear(self, **kwargs):
        """Clears the Copilot context"""
        from pieces._vendor.pieces_os_client.models.seeds import Seeds
        from pieces._vendor.pieces_os_client.models.assets import Assets
        from pieces._vendor.pieces_os_client.models.anchors import Anchors
        from pieces._vendor.pieces_os_client.models.flattened_conversation_messages import (
            FlattenedConversationMessages,
        )

        self.raw_assets.clear(_notifiy=kwargs.get("_notifiy", True))
        self.paths.clear(_notifiy=kwargs.get("_notifiy", True))
        self.assets.clear(_notifiy=kwargs.get("_notifiy", True))
        self.messages.clear(_notifiy=kwargs.get("_notifiy", True))
        self._paths = Anchors(iterable=[])
        self._assets = Assets(iterable=[])
        self._raw_assets = Seeds(iterable=[])
        self._messages = FlattenedConversationMessages(iterable=[])

    def _get_relevant_dict(self):
        return {
            "anchors": self._paths if self.paths else None,
            "seed": self._raw_assets if self.raw_assets else None,
            "assets": self._assets if self.assets else None,
            "messages": self._messages if self.messages else None,
            "temporal": self._temporal() if self.ltm.is_chat_ltm_enabled else None,
        }

    def _temporal(self) -> Optional["TemporalRangeGrounding"]:
        from pieces._vendor.pieces_os_client.models.temporal_range_grounding import (
            TemporalRangeGrounding,
        )
        from pieces._vendor.pieces_os_client.models.flattened_ranges import FlattenedRanges
        from pieces._vendor.pieces_os_client.models.referenced_range import ReferencedRange

        try:
            idx = self.copilot.chat.conversation.grounding.temporal.workstreams.indices
        except AttributeError:
            return
        return TemporalRangeGrounding(
            workstreams=FlattenedRanges(
                iterable=[ReferencedRange(id=k) for k in idx if k]
            )
        )

    def _check_relevant_existence(self) -> bool:
        return bool(self.paths or self.assets or self.raw_assets)

    def _add_message(self, message):
        from .basic_identifier.message import BasicMessage

        if not isinstance(message, BasicMessage):
            raise ValueError("Message should be BasicMessage type")
        if not self.copilot.chat:
            self.copilot.create_chat()
        self._messages.iterable.append(message.message)
        self.copilot.chat.associate_message(message)

    def _remove_message(self, index: int):
        message = self._messages.iterable.pop(index)
        self.copilot.chat.disassociate_message(
            BasicMessage(self.pieces_client, message.id)
        )

    def _add_asset(self, asset):
        from .basic_identifier.asset import BasicAsset

        if not isinstance(asset, BasicAsset):
            raise ValueError("Snippet content should be BasicAsset type")
        if not self.copilot.chat:
            self.copilot.create_chat()
        self._assets.iterable.append(asset.asset)
        self.copilot.chat.associate_asset(asset)

    def _remove_asset(self, index: int):
        from .basic_identifier.asset import BasicAsset

        asset = self._assets.iterable.pop(index)
        self.copilot.chat.disassociate_asset(BasicAsset(asset.id))

    def _add_path(self, path):
        from .basic_identifier.anchor import BasicAnchor

        if not os.path.exists(path):
            raise ValueError("Invalid path in the context")
        if not self.copilot.chat:
            self.copilot.create_chat()
        anchor = BasicAnchor.from_raw_content(path)
        self._paths.iterable.append(anchor.anchor)
        self.copilot.chat.associate_anchor(anchor)

    def _remove_path(self, index: int):
        from .basic_identifier.anchor import BasicAnchor

        anchor = self._paths.iterable.pop(index)
        self.copilot.chat.disassociate_anchor(BasicAnchor(anchor.id))

    def _add_raw_asset(self, asset: str):
        from .basic_identifier.asset import BasicAsset

        if not isinstance(asset, str):
            raise ValueError("Raw snippet content should be string type")
        self._raw_assets.iterable.append(BasicAsset._get_seed(asset))

    def _remove_raw_asset(self, index: int):
        self._raw_assets.iterable.pop(index)

    def _init(self, chat: "BasicChat"):
        from .basic_identifier.anchor import BasicAnchor

        self.clear(_notifiy=False)
        self.assets.extend(
            chat._from_indices(
                getattr(chat.conversation.assets, "indices", {}),
                lambda id: BasicAsset(id),
            )
        )
        ls = chat._from_indices(
            getattr(chat.conversation.anchors, "indices", {}),
            lambda id: BasicAnchor(id).fullpath,
        )
        ls = [item for sublist in ls for item in sublist]

        self.paths.extend(ls)
