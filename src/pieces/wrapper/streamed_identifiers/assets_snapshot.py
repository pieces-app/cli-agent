import threading
from ._streamed_identifiers import StreamedIdentifiersCache

class AssetSnapshot(StreamedIdentifiersCache):
	"""
	A class to represent a snapshot of all the cached Assets.
	"""
	_initialized:threading.Event

	@classmethod
	def _api_call(cls, id):
		asset = cls.pieces_client.asset_api.asset_snapshot(id)
		# cls.on_update(asset)
		return asset


	@staticmethod
	def _sort_first_shot():
		pass
	
