import os
from typing import List, Optional, TYPE_CHECKING

from pieces._vendor.pieces_os_client.models.anchor_type_enum import AnchorTypeEnum

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.anchor import Anchor
    from .chat import BasicChat
    from .anchor import BasicAnchor
    from .message import BasicMessage
    from .asset import BasicAsset

from ..streamed_identifiers.anchor_snapshot import AnchorSnapshot

from .basic import Basic


class BasicAnchor(Basic):
    """
    A class to represent a basic anchor, initialized with an anchor ID.
    """

    @property
    def anchor(self) -> "Anchor":
        """
        Gets the Anchor instance of the anchor.

        Returns:
                The Anchor instance of the anchor.
        """
        anchor = AnchorSnapshot.identifiers_snapshot.get(self._id)
        if not anchor:
            raise ValueError("Anchor not found")
        return anchor

    @property
    def id(self) -> str:
        """
        Gets the ID of the anchor.

        Returns:
                The ID of the anchor.
        """
        return self.anchor.id

    @property
    def name(self) -> str:
        """
        Gets the name of the Anchor.

        Returns:
                returns the name of the Anchor
        """
        return self.anchor.name

    @name.setter
    def name(self, name):
        """
        Sets the name of the anchor.

        Args:
                name: The new name of the anchor.
        """
        self.anchor.name = name
        self._edit_anchor(self.anchor)

    def delete(self):
        """
        Deletes an Anchor.
        """
        AnchorSnapshot.pieces_client.anchors_api.anchors_delete_specific_anchor(self.id)

    @classmethod
    def create(cls, type: AnchorTypeEnum, path: str) -> "BasicAnchor":
        """
        Creates an Anchor.

        Args:
                type: The type of the anchor. (FILE or DIRECTORY)
                path: The path of the anchor.

        Returns:
                The created BasicAnchor instance.
        """

        from pieces._vendor.pieces_os_client.models.seeded_anchor import SeededAnchor

        anchor = AnchorSnapshot.pieces_client.anchors_api.anchors_create_new_anchor(
            False, seeded_anchor=SeededAnchor(type=type, fullpath=path)
        )
        AnchorSnapshot.identifiers_snapshot[anchor.id] = (
            anchor  # Update the local cache
        )
        return BasicAnchor(anchor.id)

    @staticmethod
    def _edit_anchor(anchor):
        """
        Edits the anchor.

        Args:
                anchor: The anchor to edit.
        """
        AnchorSnapshot.pieces_client.anchor_api.anchor_update(False, anchor)

    @property
    def type(self) -> AnchorTypeEnum:
        """
        Gets the type of the anchor.

        Returns:
                The type of the anchor.
        """
        return self.anchor.type

    @property
    def fullpath(self) -> List[str]:
        """
        Gets the fullpath of the anchor.

        Returns:
                The fullpath of the anchor.
        """
        return [
            point.reference.fullpath
            for point in self.anchor.points.iterable
            if point.reference and point.reference.fullpath
        ]

    @classmethod
    def exists(cls, paths: List[str]) -> Optional["BasicAnchor"]:
        """
        Checks if an anchor exists.

        Args:
                paths: The paths to check.

        Returns:
                The existing anchor if found, otherwise None.
        """
        for anchor in AnchorSnapshot.identifiers_snapshot.keys():
            a = BasicAnchor(anchor)
            if a.fullpath == paths:
                return BasicAnchor(a.id)

    @property
    def assets(self) -> Optional[List["BasicAsset"]]:
        """
        Gets the assets of the anchor.

        Returns:
                The assets of the anchor.
        """
        return (
            [(asset.id) for asset in self.anchor.assets.iterable]
            if self.anchor.assets
            else None
        )

    @property
    def chats(self) -> Optional[List["BasicChat"]]:
        """
        Gets the chats of the anchor.

        Returns:
                The chats of the anchor.
        """
        from .chat import BasicChat

        return (
            [BasicChat(chat.id) for chat in self.anchor.conversations.iterable]
            if self.anchor.conversations
            else None
        )

    @property
    def messages(self) -> Optional[List["BasicMessage"]]:
        """
        Gets the messages of the anchor.

        Returns:
                The messages of the anchor.
        """
        from .message import BasicMessage

        return (
            [BasicMessage(message.id) for message in self.anchor.messages.iterable]
            if self.anchor.messages
            else None
        )

    @classmethod
    def from_raw_content(cls, path: str) -> "BasicAnchor":
        """
        Creates a BasicAnchor from the raw content.
        If found an anchor exists it will not create one.

        Args:
                path (str): The path of the anchor.

        Returns:
                The created BasicAnchor instance.
        """
        anchor = cls.exists([path])
        if anchor:
            return anchor
        else:
            anchor_type = (
                AnchorTypeEnum.DIRECTORY if os.path.isdir(path) else AnchorTypeEnum.FILE
            )
            return cls.create(anchor_type, path)

    def associate_chat(self, chat: "BasicChat"):
        """
        Associates a chat with the anchor.

        Args:
                chat: The BasicChat object to associate.
        """
        AnchorSnapshot.pieces_client.anchor_api.anchor_associate_conversation(
            chat.id, self.anchor.id
        )

    def disassociate_chat(self, chat: "BasicChat"):
        """
        Disassociates a chat from the anchor.

        Args:
                chat: The BasicChat object to disassociate.
        """
        AnchorSnapshot.pieces_client.anchor_api.anchor_disassociate_conversation(
            chat.id, self.anchor.id
        )
