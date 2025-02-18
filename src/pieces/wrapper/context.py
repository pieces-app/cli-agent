from typing import TYPE_CHECKING, List
import os

if TYPE_CHECKING:
	from .basic_identifier.asset import BasicAsset
	from .basic_identifier.message import BasicMessage
	from . import PiecesClient

class Context:
	def __init__(self,
		pieces_client:"PiecesClient",
		paths:List[str] = [],
		raw_assets:List[str] = [],
		assets:List["BasicAsset"] = [],
		messages:List["BasicMessage"] = []):
		self.pieces_client = pieces_client
		self.raw_assets = raw_assets
		self.paths = paths
		self.assets = assets
		self.messages = messages

	def clear(self):
		self.raw_assets = []
		self.paths = []
		self.assets = []
		self.messages = []

	def _get_relevant_dict(self):
		self._check_paths(self.paths)
		assets = self._check_assets(self.assets)
		raw_snippet = self._check_raw_assets(self.raw_assets)
		messages = self._check_messages(self.messages)

		return {
			"paths":self.paths,
			"seed":raw_snippet,
			"assets":assets,
			"messages":messages
		}

	def _check_relevant_existence(self) -> bool:
		return bool(self.paths or self.assets or self.raw_assets)

	@staticmethod
	def _check_messages(messages):
		from pieces_os_client.models.flattened_conversation_messages import FlattenedConversationMessages
		from .basic_identifier.message import BasicMessage 
		message_list = FlattenedConversationMessages(iterable=[])
		for message in messages:
			if not isinstance(message,BasicMessage):
				raise ValueError("Invalid message type")
			message_list.iterable.append(message.message)
		return message_list

	@staticmethod
	def _check_assets(assets):
		from pieces_os_client.models.flattened_assets import FlattenedAssets
		from .basic_identifier.asset import BasicAsset
		assets_list = FlattenedAssets(iterable=[])
		for snippet in assets:
			if not isinstance(snippet,BasicAsset):
				raise ValueError("Invalid asset type")
			assets_list.iterable.append(snippet.asset)
		return assets_list

	@staticmethod
	def _check_paths(paths):
		for path in paths:
			if not os.path.exists(path):
				raise ValueError("Invalid path in the context")

	@staticmethod
	def _check_raw_assets(assets:List[str]):
		from pieces_os_client.models.seeds import Seeds
		seed_list = Seeds(iterable=[])
		for raw in assets:
			if not isinstance(raw,str):
				raise ValueError("Raw material content should be string type")
			seed_list.iterable.append(BasicAsset._get_seed(raw))
		return seed_list

	def _relevance_api(self,query):
		from pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
		return self.pieces_client.qgpt_api.relevance(
			QGPTRelevanceInput(
				query=query,
				application=self.pieces_client.application.id,
				model=self.pieces_client.model_id,
				**self._get_relevant_dict()
			)).relevant