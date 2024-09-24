from typing import TYPE_CHECKING, List, Optional

from pieces_os_client.models.existent_metadata import ExistentMetadata
from pieces_os_client.models.seeded_website import SeededWebsite
from pieces_os_client.models.website import Website

from .basic import Basic

if TYPE_CHECKING:
	from . import BasicAsset, BasicChat
	from ..client import PiecesClient


class BasicWebsite(Basic):
	"""
	Represents a basic website in the Pieces system.

	Attributes:
	- website: The website object associated with this BasicWebsite.
	- pieces_client: The PiecesClient object used to interact with the Pieces system.
	"""

	def __init__(self, pieces_client: "PiecesClient", website: Website) -> None:
		"""
		Initializes a BasicWebsite object.

		Args:
		- pieces_client: The PiecesClient object.
		- website: The website object.
		"""
		self.website = website
		self.pieces_client = pieces_client

		
	@classmethod
	def from_id(cls,pieces_client: "PiecesClient",id:str):
		"""
		Args:
		- pieces_client: The PiecesClient object.
		- id: The ID of the website.

		Raises:
		- ValueError: If there is an error retrieving the website.
		"""
		try:
			website = pieces_client.website_api.websites_specific_website_snapshot(
				id, transferables=True)
			return BasicWebsite(pieces_client,website)
		except:
			raise ValueError("Error in retrieving the website")


	@staticmethod
	def create(pieces_client: "PiecesClient", seeded_website: SeededWebsite) -> "BasicWebsite":
		"""
		Creates a new website in the Pieces system.

		Args:
		- pieces_client: The PiecesClient object.
		- seeded_website: The SeededWebsite object for the new website.

		Returns:
		- BasicWebsite: The newly created BasicWebsite object.
		"""
		return BasicWebsite(pieces_client,
			pieces_client.websites_api.websites_create_new_website(
				transferables=False,
				seeded_website=seeded_website)
			)


	@staticmethod
	def exists(pieces_client: "PiecesClient", url:str) -> Optional["BasicWebsite"]:
		"""
		Checks if a website exists in the Pieces system.

		Args:
		- pieces_client: The PiecesClient object.
		- url: The URL of the website.

		Returns:
		- BasicWebsite: The existing BasicWebsite object if found, None otherwise.
		"""
		existance = pieces_client.websites_api.websites_exists(
			ExistentMetadata(
				value=url
			))
		if existance.website:
			return BasicWebsite.from_id(pieces_client,existance.website.id)


	@classmethod
	def from_raw_content(cls, pieces_client: "PiecesClient", url: str) -> "BasicWebsite":
		"""
		Retrieves a BasicWebsite object based on raw content.

		Args:
		- pieces_client: The PiecesClient object.
		- url: The URL of the website.

		Returns:
		- BasicWebsite: The BasicWebsite object associated with the URL.
		"""
		website = cls.exists(pieces_client,url)
		return website if website else cls.create(
				pieces_client,
				SeededWebsite(url=url,name=url)
			)

	@property
	def name(self) -> str:
		"""
		Getter for the name of the website.

		Returns:
		- str: The name of the website.
		"""
		return self.website.name

	@name.setter
	def name(self, name):
		"""
		Setter for the name of the website.

		Args:
		- name: The new name for the website.
		"""
		self.website.name = name
		self._edit_website(self.website)

	@property
	def id(self) -> str:
		"""
		Getter for the ID of the website.

		Returns:
		- str: The ID of the website.
		"""
		return self.website.id

	@property
	def url(self) -> str:
		"""
		Getter for the URL of the website.

		Returns:
		- str: The URL of the website.
		"""
		return self.website.url

	@url.setter
	def url(self, url):
		"""
		Setter for the URL of the website.

		Args:
		- url: The new URL for the website.
		"""
		self.website.text = url
		self._edit_website(self.website)

	@property
	def assets(self) -> Optional[List["BasicAsset"]]:
		"""
		Getter for the assets associated with the website.

		Returns:
		- List[BasicAsset]: The list of BasicAsset objects associated with the website.
		"""
		from . import BasicAsset
		if self.website.assets and self.website.assets.iterable:
			return [BasicAsset(asset.id) for asset in self.website.assets.iterable]

	@property
	def chats(self) -> Optional[List["BasicChat"]]:
		"""
		Getter for the chats associated with the website.

		Returns:
		- List[BasicChat]: The list of BasicChat objects associated with the website.
		"""
		from . import BasicChat
		if self.website.conversations and self.website.conversations.iterable:
			return [BasicChat(chat.id) for chat in self.website.conversations.iterable]

	def associate_asset(self, asset: "BasicAsset"):
		"""
		Associates an asset with the website.

		Args:
		- asset: The BasicAsset object to associate.
		"""
		self.pieces_client.website_api.website_associate_asset(asset.id,self.website.id)

	def disassociate_asset(self, asset: "BasicAsset"):
		"""
		Disassociates an asset from the website.

		Args:
		- asset: The BasicAsset object to disassociate.
		"""
		self.pieces_client.website_api.website_disassociate_asset(self.website.id,asset.id)

	def associate_chat(self, chat: "BasicChat"):
		"""
		Associates a chat with the website.

		Args:
		- chat: The BasicChat object to associate.
		"""
		self.pieces_client.website_api.website_associate_conversation(chat.id,self.website.id)

	def disassociate_chat(self, chat: "BasicChat"):
		"""
		Disassociates a website from a chat.

		Args:
		- chat: The BasicChat object to disassociate.
		"""
		self.pieces_client.website_api.website_disassociate_conversation(self.website.id,chat.id)

	def delete(self):
		"""
		Deletes the website from the Pieces OS.
		"""
		self.pieces_client.websites_api.websites_delete_specific_website(self.website.id)

	def _edit_website(self, website: Website):
		"""
		Edits the website in the Pieces OS.

		Args:
		- website: The Website object to edit.
		"""
		return self.pieces_client.website_api.website_update(False,website)

