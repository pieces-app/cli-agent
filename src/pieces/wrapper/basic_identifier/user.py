import threading
from typing import Optional
from .basic import Basic

from pieces_os_client.models.user_profile import UserProfile
from pieces_os_client.models.allocation_status_enum import AllocationStatusEnum

class BasicUser(Basic):
	"""
	A class to represent a basic user and manage their connection to the cloud.

	Attributes:
		user_profile: The profile of the user.
		pieces_client: The client used to interact with the pieces OS API.
	"""

	user_profile: Optional[UserProfile] = None

	def __init__(self, pieces_client) -> None:
		"""
		Initializes the BasicUser with a pieces client.

		Args:
			pieces_client: The client used to interact with the pieces OS API.
		"""
		self.pieces_client = pieces_client
	

	@property
	def id(self) -> Optional[str]:
		if self.user_profile:
			return self.user_profile.id


	def on_user_callback(self, user: Optional[UserProfile], connecting=False):
		"""
		Callback function to set the user profile.

		Args:
			user: The profile of the user.
			connecting: A flag indicating if the user is connecting to the cloud (default is False).
		"""
		self.user_profile = user

	def _on_login_connect(self, thread, timeout):
		"""
		Waits for the user to login and then connects to the cloud.

		Args:
			thread: The thread handling the login process.
			timeout: The maximum time to wait for the login process.
		"""
		thread.get(timeout)  # Wait for the user to login
		self.connect()

	def login(self, connect_after_login=True, timeout=120):
		"""
		Logs the user into the OS and optionally connects to the cloud.

		Args:
			connect_after_login: A flag indicating if the user should connect to the cloud after login (default is True).
			timeout: The maximum time to wait for the login process (default is 120 seconds).
		"""
		thread = self.pieces_client.os_api.sign_into_os(async_req=True)
		if connect_after_login:
			threading.Thread(target=lambda: self._on_login_connect(thread, timeout))

	def logout(self):
		"""
		Logs the user out of the OS.
		"""
		self.pieces_client.os_api.sign_out_of_os()

	def connect(self):
		"""
		Connects the user to the cloud.

		Raises:
			PermissionError: If the user is not logged in.
		"""
		if not self.user_profile:
			raise PermissionError("You must be logged in to use this feature")
		self.on_user_callback(self.user_profile, True)  # Set the connecting to cloud bool to true
		self.pieces_client.allocations_api.allocations_connect_new_cloud(self.user_profile)

	def disconnect(self):
		"""
		Disconnects the user from the cloud.

		Raises:
			PermissionError: If the user is not logged in.
		"""
		if not self.user_profile:
			raise PermissionError("You must be logged in to use this feature")
		if self.user_profile.allocation:  # Check if there is an allocation iterable
			self.pieces_client.allocations_api.allocations_disconnect_cloud(self.user_profile.allocation)

	@property
	def picture(self) -> Optional[str]:
		"""
		Returns the user's profile picture URL.

		Returns:
			The URL of the user's profile picture, or None if not available.
		"""
		if self.user_profile:
			return self.user_profile.picture


	@property
	def name(self) -> Optional[str]:
		"""
		Returns the name of the user.

		Returns:
			Optional[str]: The name of the user if the user logged in, otherwise None.
		"""
		if self.user_profile:
			return self.user_profile.name

	@property
	def email(self) -> Optional[str]:
		"""
		Returns the email of the user.

		Returns:
			Optional[str]: The email of the user if the user logged in, otherwise None.
		"""
		if self.user_profile:
			return self.user_profile.email

	@property
	def vanity_name(self) -> Optional[str]: # TODO: implements the setter object
		"""
		Returns the vanity name of the user which is the base name of the cloud url.
			For example, if the cloud URL is 'bishoyatpieces.pieces.cloud', this method returns 'bishoyatpieces'.

		Returns:
			Optional[str]: The vanity name of the user if the user user logged in and connected to the cloud, otherwise None.
		"""
		if self.user_profile:
			return self.user_profile.vanityname

	@property
	def cloud_status(self) -> Optional[AllocationStatusEnum]:
		"""
		Returns the cloud status of the user's cloud.

		Returns:
			Optional[AllocationStatusEnum]: The cloud status of the user's cloud.
		"""
		if self.user_profile and self.user_profile.allocation:
			return self.user_profile.allocation.status.cloud

	def __repr__(self):
		return f"<{self.__class__.__name__}(pieces_client={self.pieces_client})>"