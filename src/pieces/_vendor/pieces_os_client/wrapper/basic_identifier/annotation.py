from typing import TYPE_CHECKING, Optional

from .basic import Basic

if TYPE_CHECKING:
	from pieces._vendor.pieces_os_client.models.annotation import Annotation
	from pieces._vendor.pieces_os_client.models.annotation_type_enum import AnnotationTypeEnum
	from pieces._vendor.pieces_os_client.models.seeded_annotation import SeededAnnotation
	from .asset import BasicAsset
	from .chat import BasicChat
	from ..client import PiecesClient

class BasicAnnotation(Basic):
	"""
	A class representing a basic annotation in the system.

	Attributes:
		pieces_client (PiecesClient): The client object used to interact with the API.
		annotation (Annotation): The annotation object associated with the basic annotation.
	"""

	def __init__(self, pieces_client: "PiecesClient", annotation: "Annotation") -> None:
		"""
		Initializes a BasicAnnotation object.

		Args:
			pieces_client (PiecesClient): The client object used to interact with the API.
			annotation (Annotation): The annotation object associated with the basic annotation.
		"""
		self.pieces_client = pieces_client
		self.annotation = annotation
		super().__init__(annotation.id)

	@property
	def id(self):
		"""
		Returns the ID of the annotation.

		Returns:
			The ID of the annotation.
		"""
		return self.annotation.id

	@staticmethod
	def from_id(pieces_client: "PiecesClient", id) -> "BasicAnnotation":
		"""
		Creates a BasicAnnotation object from the given ID.

		Args:
			pieces_client (PiecesClient): The client object used to interact with the API.
			id: The ID of the annotation.

		Returns:
			A BasicAnnotation object.
		"""
		return BasicAnnotation(pieces_client, pieces_client.annotation_api.annotation_specific_annotation_snapshot(id))

	@property
	def type(self) -> "AnnotationTypeEnum":
		"""
		Returns the type of the annotation.

		Returns:
			The type of the annotation.
		"""
		return self.annotation.type

	@property
	def raw_content(self):
		"""
		Returns the raw content of the annotation.

		Returns:
			The raw content of the annotation.
		"""
		return self.annotation.text

	@raw_content.setter
	def raw_content(self, t):
		"""
		Sets the raw content of the annotation.

		Args:
			t: The raw content to be set.
		"""
		self.annotation.text = t
		self._edit_annotation(self.annotation)

	@property
	def asset(self) -> Optional["BasicAsset"]:
		"""
		Returns the asset associated with the annotation.

		Returns:
			The asset associated with the annotation.
		"""
		from .asset import BasicAsset
		if self.annotation.asset:
			return BasicAsset(self.annotation.asset.id)

	@property
	def chat(self) -> Optional["BasicChat"]:
		"""
		Returns the chat associated with the annotation.

		Returns:
			The chat associated with the annotation.
		"""
		from .chat import BasicChat
		if self.annotation.conversation:
			return BasicChat(self.annotation.conversation.id)

	@staticmethod
	def create(pieces_client, seeded_annotation: "SeededAnnotation") -> "BasicAnnotation":
		"""
		Creates a new annotation based on the seeded annotation.

		Args:
			pieces_client: The client object used to interact with the API.
			seeded_annotation (SeededAnnotation): The seeded annotation to create the new annotation.

		Returns:
			A BasicAnnotation object.
		"""
		return BasicAnnotation(
			pieces_client,
			pieces_client.annotations_api.annotations_create_new_annotation(
				seeded_annotation
			))

	def delete(self) -> None:
		"""
		Deletes the annotation.
		"""
		self.pieces_client.annotations_api.annotations_delete_specific_annotation(self.annotation.id)


	def _edit_annotation(self, annotation: "Annotation"):
		"""
		Edits the given annotation.

		Args:
			annotation (Annotation): The annotation to be edited.
		"""
		self.pieces_client.annotation_api.annotation_update(annotation)

