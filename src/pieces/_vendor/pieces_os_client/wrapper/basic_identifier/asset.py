from ..streamed_identifiers.assets_snapshot import AssetSnapshot
from .basic import Basic
from typing import Literal, Optional, List, TYPE_CHECKING

from pieces._vendor.pieces_os_client.models.classification_specific_enum import ClassificationSpecificEnum
from pieces._vendor.pieces_os_client.models.classification_generic_enum import ClassificationGenericEnum

if TYPE_CHECKING:
	from pieces._vendor.pieces_os_client.models.fragment_metadata import FragmentMetadata
	from pieces._vendor.pieces_os_client.models.format import Format
	from pieces._vendor.pieces_os_client.models.shares import Shares
	from pieces._vendor.pieces_os_client.models.asset import Asset
	from pieces._vendor.pieces_os_client.models.seed import Seed
	from .annotation import BasicAnnotation
	from .tag import BasicTag
	from .website import BasicWebsite

# Friendly wrapper (to avoid interacting with the pieces_os_client sdks models)

class BasicAsset(Basic):
	"""
	A wrapper class for managing assets.
	"""
	@classmethod
	def identifiers_snapshot(cls):
		if AssetSnapshot.identifiers_snapshot:
			return AssetSnapshot.identifiers_snapshot
		
		AssetSnapshot.identifiers_snapshot = {item.id:None for item in cls.get_identifiers()}

		return AssetSnapshot.identifiers_snapshot
	
	@staticmethod
	def get_identifiers():
		"""
			:returns: The assets id
		"""
		assets_api = AssetSnapshot.pieces_client.assets_api
		api_response = assets_api.assets_identifiers_snapshot()
		return api_response.iterable
		
	@property
	def asset(self) -> "Asset":
		asset = AssetSnapshot.identifiers_snapshot.get(self._id)
		if not asset:
			asset = AssetSnapshot.update_identifier(self._id)
		return asset

	@property
	def id(self) -> str:
		"""
			:returns: The asset id
		"""
		return self.asset.id

	@property
	def created_at(self):
		return self.asset.created.readable if self.asset.created.readable else "Unknown"

	@property
	def updated_at(self):
		return self.asset.updated.readable if self.asset.updated.readable else "Unknown"
	
	@property
	def raw_content(self) -> Optional[str]:
		"""
		Get the raw content of the asset.

		Returns:
			Optional[str]: The raw content if available, otherwise None.

		Raises:
			ValueError: If unable to get OCR content for an image.
		"""
		if self.is_image:
			content = self._get_ocr_content()
			if content is None:
				raise ValueError('Unable to get OCR content')
			return content
		else:
			try:
				fragment_raw = self.asset.original.reference.fragment.string.raw
			except AttributeError:
				fragment_raw = ""
			try:
				preview_raw = self.asset.preview.base.reference.fragment.string.raw
			except AttributeError:
				preview_raw = ""

			return preview_raw or fragment_raw or ''

	@raw_content.setter
	def raw_content(self, content: str):
		"""
		Edit the original format of the asset.

		Args:
			content: The new content to be set.
		"""
		format_api = AssetSnapshot.pieces_client.format_api
		original = None
		if self.is_image:
			original = self._get_ocr_format(self.asset)
		if not original:
			original = format_api.format_snapshot(self.asset.original.id, transferable=True)

		if original.fragment and original.fragment.string and original.fragment.string.raw:
			original.fragment.string.raw = content
		elif original.file and original.file.string and original.file.string.raw:
			original.file.string.raw = content
		elif original.file and original.file.bytes and original.file.bytes.raw:
			original.file.bytes.raw =  list(content.encode('utf-8'))

		format_api.format_update_value(transferable=False, format=original)

	@property
	def type(self) -> ClassificationGenericEnum:
		return self.asset.original.reference.classification.generic

	@property
	def is_image(self) -> bool:
		"""
		Check if the asset is an image.

		Returns:
			bool: True if the asset is an image, otherwise False.
		"""
		return (
			self.type ==
			ClassificationGenericEnum.IMAGE
		)


	@property
	def classification(self) -> Optional[ClassificationSpecificEnum]:
		"""
		Get the specific classification of the asset (eg: py).

		:return: The classification value of the asset, or None if not available.
		"""
		if self.is_image:
			ocr_format = self._get_ocr_format(self.asset)
			if ocr_format:
				return ocr_format.classification.specific
		return self.asset.original.reference.classification.specific

	@classification.setter
	def classification(self, classification):
		"""
		Reclassify the classification attribute.

		Args:
			classification (str or ClassificationSpecificEnum): The new classification value.

		Raises:
			ValueError: If the classification is not a string or ClassificationSpecificEnum.
			NotImplementedError: If the asset is an image, reclassification is not supported.
		"""
		from pieces._vendor.pieces_os_client.models.asset_reclassification import AssetReclassification
		if isinstance(classification, str):
			if classification not in ClassificationSpecificEnum:
				raise ValueError(f"Classification must be one from {list(ClassificationSpecificEnum)}")
			classification = ClassificationSpecificEnum(classification)

		if not isinstance(classification, ClassificationSpecificEnum):
			raise ValueError("Invalid classification")

		if self.is_image:
			raise NotImplementedError("Error in reclassify asset: Image reclassification is not supported")

		AssetSnapshot.pieces_client.asset_api.asset_reclassify(
			asset_reclassification=AssetReclassification(
				ext=classification, asset=self.asset),
			transferables=False
		)



	@property
	def name(self) -> str:
		"""
		Get the name of the asset.

		Returns:
			str: The name of the asset if available, otherwise "Unnamed snippet".
		"""
		return self.asset.name if self.asset.name else "Unnamed material"
	
	@name.setter
	def name(self, name: str):
		"""
		Edit the name of the asset.

		:param name: The new name to be set for the asset.
		"""
		self.asset.name = name
		self._edit_asset(self.asset)

	@property
	def description(self) -> Optional[str]:
		"""
		Retrieve the description of the asset.

		:return: The description text of the asset, or None if not available.
		"""
		annotations = self.annotations
		if not annotations:
			return
		d = None
		for annotation in annotations:
			if annotation.type == "DESCRIPTION":
				d = annotation
		
		return d.raw_content if d else None


	@property
	def annotations(self) -> Optional[List["BasicAnnotation"]]:
		"""
		Get all annotations of the asset.

		Returns:
			Optional[Annotations]: The annotations if available, otherwise None.
		"""
		from .annotation import BasicAnnotation
		if self.asset.annotations:
			return [BasicAnnotation(AssetSnapshot.pieces_client,a) for a in self.asset.annotations.iterable]


	def delete(self) -> None:
		"""
		Delete the asset.
		"""
		AssetSnapshot.pieces_client.assets_api.assets_delete_asset(self.id)

	@classmethod
	def create(cls,raw_content: str, metadata: Optional["FragmentMetadata"] = None) -> str:
		"""
		Create a new asset.

		Args:
			raw_content (str): The raw content of the asset.
			metadata (Optional[FragmentMetadata]): The metadata of the asset.

		Returns:
			str: The ID of the created asset.
		"""
		seed = cls._get_seed(raw_content,metadata)

		created_asset_id = AssetSnapshot.pieces_client.assets_api.assets_create_new_asset(transferables=False, seed=seed).id
		return created_asset_id

	def share(self) -> "Shares":
		"""
		Generates a shareable link for the given asset.

		Raises:
		PermissionError: If the user is not logged in or is not connected to the cloud.
		"""
		return self._share(self.asset)


	@classmethod
	def share_raw_content(cls,raw_content:str) -> "Shares":
		"""
		Generates a shareable link for the given user raw content.
		Note: this will create an asset

		Args:
			raw_content (str): The raw content of the asset that will be shared.

		Raises:
		PermissionError: If the user is not logged in or is not connected to the cloud.
		"""
		return cls._share(seed = cls._get_seed(raw_content))

	@property
	def tags(self) -> Optional[List["BasicTag"]]:
		"""
		Get all the tags associate with the asset

		returns a list of BasicTag if there is a tag associated else None
		"""
		from .tag import BasicTag
		if self.asset.tags and self.asset.tags.iterable:
			return [BasicTag(AssetSnapshot.pieces_client,tag) for tag in self.asset.tags.iterable]

	@property
	def markdown(self) -> Optional[str]:
		"""
			returns the asset as a markdown containing the content
			all tags wesites and other metadata
		"""
		res = AssetSnapshot.pieces_client.asset_api.asset_specific_asset_export(self.asset.id,"MD")
		if res.raw.string:
			return res.raw.string.raw

	@property
	def websites(self) -> Optional[List["BasicWebsite"]]:
		from .website import BasicWebsite
		if self.asset.websites:
			return [
				BasicWebsite(AssetSnapshot.pieces_client,webstie) 
				for webstie in self.asset.websites.iterable
			]

	@staticmethod
	def search(query:str,search_type:Literal["fts","ncs","fuzzy"] = "fts") -> Optional[List["BasicAsset"]]:
		"""
		Perform a search using either Full Text Search (FTS) or Neural Code Search (NCS) or Fuzzy search (fuzzy).
		
		Parameters:
			query (str): The search query string.
			search_type (Literal["fts", "ncs", "fuzzy"], optional): The type of search to perform.
				'fts' for Full Text Search (default) or 'ncs' for Neural Code Search.
		
		Returns:
			Optional[List["BasicAsset"]]: A list of search results or None if no results are found.
		"""
		if search_type == 'ncs':
			results = AssetSnapshot.pieces_client.search_api.neural_code_search(query=query)
		elif search_type == 'fts':
			results = AssetSnapshot.pieces_client.search_api.full_text_search(query=query)
		elif search_type == "fuzzy":
			results = AssetSnapshot.pieces_client.assets_api.search_assets(query=query,transferables=False)

		if results:
			# Extract the iterable which contains the search results
			iterable_list = results.iterable if hasattr(results, 'iterable') else []

			# Check if iterable_list is a list and contains SearchedAsset objects
			if isinstance(iterable_list, list) and all(hasattr(asset, 'exact') and hasattr(asset, 'identifier') for asset in iterable_list):
				# Extracting suggested and exact IDs
				suggested_ids = [asset.identifier for asset in iterable_list if not asset.exact]
				exact_ids = [asset.identifier for asset in iterable_list if asset.exact]

				# Combine and store best and suggested matches in asset_ids
				combined_ids = exact_ids + suggested_ids

				# Print the combined asset details
				if combined_ids:
					return [BasicAsset(id) for id in combined_ids]

	@staticmethod
	def _get_seed(raw: str, metadata: Optional["FragmentMetadata"] = None) -> "Seed":
		from pieces._vendor.pieces_os_client.models.seeded_asset import SeededAsset
		from pieces._vendor.pieces_os_client.models.seed import Seed
		from pieces._vendor.pieces_os_client.models.seeded_format import SeededFormat
		from pieces._vendor.pieces_os_client.models.seeded_fragment import SeededFragment
		from pieces._vendor.pieces_os_client.models.transferable_string import TransferableString
		return Seed(
			asset=SeededAsset(
				application=AssetSnapshot.pieces_client.application,
				format=SeededFormat(
					fragment=SeededFragment(
						string=TransferableString(raw=raw),
						metadata=metadata
					)
				),
				metadata=None
			),
			type="SEEDED_ASSET"
		)

	def _get_ocr_content(self) -> Optional[str]:
		"""
		Get the OCR content of the asset.

		Returns:
			Optional[str]: The OCR content if available, otherwise None.
		"""
		if not self.asset:
			return
		format = self._get_ocr_format(self.asset)
		if format is None:
			return
		return self._ocr_from_format(format)

	@staticmethod
	def _get_ocr_format(src: "Asset") -> Optional["Format"]:
		"""
		Get the OCR format of the asset.

		Args:
			src (Asset): The asset object.

		Returns:
			Optional[Format]: The OCR format if available, otherwise None.
		"""
		image_id = src.original.reference.analysis.image.ocr.raw.id if src.original and src.original.reference and src.original.reference.analysis and src.original.reference.analysis.image and src.original.reference.analysis.image.ocr and src.original.reference.analysis.image.ocr.raw and src.original.reference.analysis.image.ocr.raw.id else None
		if image_id is None:
			return None
		return next((element for element in src.formats.iterable if element.id == image_id), None)

	@staticmethod
	def _ocr_from_format(src: Optional["Format"]) -> Optional[str]:
		"""
		Extract OCR content from the format.

		Args:
			src (Optional[Format]): The format object.

		Returns:
			Optional[str]: The OCR content if available, otherwise None.
		"""
		if src is None:
			return None
		return bytes(src.file.bytes.raw).decode('utf-8')

	@staticmethod
	def _edit_asset(asset):
		AssetSnapshot.pieces_client.asset_api.asset_update(False,asset)

	@staticmethod
	def _share(asset=None,seed=None):
		"""
			You need to either give the seed or the asset_id
		"""
		from pieces._vendor.pieces_os_client.models.linkify import Linkify
		if asset:
			kwargs = {"asset" : asset}
		else:
			kwargs = {"seed" : seed}

		user = AssetSnapshot.pieces_client.user.user_profile

		if not user:
			raise PermissionError("You need to be logged in to generate a shareable link")

		if not user.allocation:
			raise PermissionError("You need to connect to the cloud to generate a shareable link")

		return AssetSnapshot.pieces_client.linkfy_api.linkify(
			linkify=Linkify(
				access="PUBLIC",
				**kwargs
				)
			)

