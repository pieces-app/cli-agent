from abc import ABC,abstractmethod
from typing import Any, Callable, Dict, Optional, List

class Basic(ABC):
	def __init__(self, id) -> None:
		"""
		Initialize the class with a given ID.

		:param id: The ID of the Object.
		"""
		self._id = id

	@property
	@abstractmethod
	def id(self) -> str:
		pass

	def _from_indices(self, indices: Dict[str, Any], object_call: Callable[[str], Any]) -> List[Any]:
		return [object_call(id)
             for id,v in indices.items() if v != -1]

	def __repr__(self):
		"""
		Returns a detailed string representation of the object.
		"""
		return f"<{self.__class__.__name__}(id={self.id})>"

	def __eq__(self, other):
		"""
		Checks equality between two instances.
		"""
		if isinstance(other, self.__class__):
			return self.id == other.id
		return False

	def __str__(self):
		"""
		Returns a user-friendly string representation of the object.
		"""
		if hasattr(self,"name"):
			return f"ID: {self.id}, Name: {self.name}"
		return f"ID: {self.id}"


	def __hash__(self):
		"""
		Returns a hash of the instance.
		"""
		return hash(self.id)

