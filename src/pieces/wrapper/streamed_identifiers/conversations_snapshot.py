import threading
from ._streamed_identifiers import StreamedIdentifiersCache

class ConversationsSnapshot(StreamedIdentifiersCache):
	"""
	A class to represent a snapshot of all the cached Conversations.
	
	Class attributes:
	identifiers_snapshot (dict): A dictionary where the keys are UUIDs (unique identifiers) and the values are Conversation objects.
	"""
	_initialized:threading.Event

	@classmethod
	def _sort_first_shot(cls):
		# Sort the dictionary by the "updated" timestamp
		sorted_conversations = sorted(cls.identifiers_snapshot.values(), key=lambda x: x.updated.value, reverse=True)
		cls.identifiers_snapshot = {conversation.id:conversation for conversation in sorted_conversations}

	@classmethod
	def _api_call(cls,id):
		con = cls.pieces_client.conversation_api.conversation_get_specific_conversation(id)
		# cls.on_update(con)
		return con
