import json
import pickle
from typing import Union,Dict,Optional
import time
import subprocess
import platform
import os
from pathlib import Path
import sys
import threading
from platformdirs import user_data_dir
import semver
from pieces import __version__
from pieces.gui import server_startup_failed, print_pieces_os_link,print_version_details

from pieces_os_client.api.well_known_api import WellKnownApi
from pieces_os_client.api.connector_api import ConnectorApi
from pieces_os_client.api.models_api import ModelsApi

from pieces_os_client.configuration import Configuration
from pieces_os_client.api_client import ApiClient

from pieces_os_client.models.application import Application
from pieces_os_client.models.seeded_connector_connection import SeededConnectorConnection
from pieces_os_client.models.seeded_tracked_application import SeededTrackedApplication
from pieces_os_client.models.application_name_enum import ApplicationNameEnum



class Settings:
	"""Settings class for the CLI Agent"""
	PIECES_OS_MIN_VERSION = "10.0.0"  # Minium version (10.0.0)
	PIECES_OS_MAX_VERSION = "11.0.0" # Maxium version (11.0.0)
	
	TIMEOUT = 20 # Websocket ask timeout 

	# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
	BASE_DIR = os.path.dirname(__file__)

	# Define the directory path
	# Check if the directory exists, if not, create it
	pieces_data_dir = user_data_dir(appauthor="pieces", appname="cli-agent",ensure_exists=True)

	models_file  = Path(
		pieces_data_dir, "model_data.pkl"
	) # model data file just store the model_id that the user is using (eg. {"model_id": UUID })

	platform_info = platform.platform()
	if 'Linux' in platform_info:
		port = 5323
	else:
		port = 1000
	
	host = f"http://127.0.0.1:{port}"
	# Defining the host is optional and defaults to http://localhost:1000
	# See configuration.py for a list of all supported configuration parameters.
	configuration = Configuration(host=host)


	# Websocket config
	BASE_WEBSOCKET_URL = host.replace('http', 'ws')
	ASK_WEBSOCKET_URL = f"{BASE_WEBSOCKET_URL}/qgpt/stream"
	ASSETS_IDENTIFIERS_WS_URL = f"{BASE_WEBSOCKET_URL}/assets/stream/identifiers"

	run_in_loop = False # is CLI looping?


	# Initialize the ApiClient globally
	api_client = ApiClient(configuration)


	# some useful directories 
	# extensions_dir
	extensions_dir = os.path.join(BASE_DIR,'commands','extensions.json')


	# open snippet directory
	open_snippet_dir = os.path.join(os.getcwd(),'opened_snippets')

	application:Application = None
	pieces_os_version:str = None
	model_name:str

	@classmethod
	def get_application(cls):
		# Call the connect api
		if cls.application:
			return cls.application
		cls.application = cls.connect_api()

	@classmethod
	def load_models(cls):
		# MODELS
		cls.models = cls.get_models_ids()
		# Check if the models file exists
		try: 
			cls.model_name,cls.model_id = cls.get_current_model_name() # Checks if the current model id is valid raise error if not vaild
		except:
			default_model_name = "GPT-3.5-turbo Chat Model"
			cls.model_id = cls.models[default_model_name]["uuid"] # default model id
			cls.dump_pickle(file = cls.models_file, model_id=cls.model_id)

	@staticmethod
	def dump_pickle(file,**data):
		"""Store data in a pickle file."""
		with open(file, 'wb') as f:
			pickle.dump(data, f)

	@classmethod
	def get_current_model_name(cls) -> str:
		with open(cls.models_file, 'rb') as f:
			model_data = pickle.load(f)
		model_id = model_data["model_id"]
		models_reverse = {v.get("uuid"):k for k,v in cls.models.items()}
		return models_reverse[model_id],model_id
	
	@classmethod
	def connect_api(cls) -> Application:
		if cls.application:
			return cls.application
		# Decide if it's Windows, Mac, Linux or Web
		local_os = platform.system().upper() if platform.system().upper() in ["WINDOWS","LINUX","DARWIN"] else "WEB"
		local_os = "MACOS" if local_os == "DARWIN" else local_os

		api_instance = ConnectorApi(cls.api_client)
		seeded_connector_connection = SeededConnectorConnection(
			application=SeededTrackedApplication(
				name = ApplicationNameEnum.OPEN_SOURCE,
				platform = local_os,
				version = __version__))
		api_response = api_instance.connect(seeded_connector_connection=seeded_connector_connection)
		cls.application = api_response.application
		return cls.application
	
	@classmethod    
	def get_models_ids(cls) -> Dict[str, Dict[str, str]]:

		api_response = ModelsApi(cls.api_client).models_snapshot()
		models = {model.name: {"uuid":model.id} for model in api_response.iterable if model.cloud or model.downloaded} # getting the models that are available in the cloud or is downloaded
		return models
	
	@classmethod
	def startup(cls):
		pieces_os_version = cls.open_pieces_os()
		if pieces_os_version:
			cls.version_check() # Check the version first 
			model_thread = threading.Thread(target=cls.load_models)
			connector_thread = threading.Thread(target=cls.connect_api)
			model_thread.start()
			connector_thread.start()
			model_thread.join() # Wait for it to finish
			connector_thread.join() # Wait for it to finish
		else:
			server_startup_failed()
			sys.exit(0) # Exit the program


	@classmethod
	def version_check(cls):
		"""Check the version of the pieces os in the within range"""
		pieces_os_version = cls.get_version()

		# Parse version numbers
		os_version_parsed = semver.VersionInfo.parse(pieces_os_version)
		min_version_parsed = semver.VersionInfo.parse(cls.PIECES_OS_MIN_VERSION)
		max_version_parsed = semver.VersionInfo.parse(cls.PIECES_OS_MAX_VERSION)

		# Check compatibility
		if os_version_parsed >= max_version_parsed:
			print("Please update your cli-agent tool. It is not compatible with the current Pieces OS version")
			print()
			print("https://pypi.org/project/pieces-cli/")
			print()
			print_version_details(pieces_os_version, __version__)
			sys.exit(0)
		elif os_version_parsed < min_version_parsed:
			print("Please update your Pieces OS. It is not compatible with the current cli-agent version")
			print()
			print_pieces_os_link()
			print()
			print_version_details(pieces_os_version, __version__)
			sys.exit(0)
			

	@classmethod
	def open_pieces_os(cls) -> Optional[str]:
		"""Open pieces os and return its version"""
		version = cls.get_version()
		if version:
			return version
		else:
			pl = platform.system()
			if pl == "Windows":
				subprocess.run(["start", "pieces://launch"], shell=True)
			elif pl == "Darwin":
				subprocess.run(["open","pieces://launch"])
			elif pl == "Linux":
				subprocess.run(["xdg-open","pieces://launch"])
			
			for _ in range(2):
				version = cls.get_version()
				if version:
					return version
				time.sleep(2) # wait for the server to open
			return cls.get_version() # pieces os version
		
	@classmethod
	def get_version(cls) -> Optional[str]:
		"""Get pieces os version return None if there is a problem"""
		if cls.pieces_os_version:
			return cls.pieces_os_version
		try:
			cls.pieces_os_version = WellKnownApi(cls.api_client).get_well_known_version()
			return cls.pieces_os_version
		except:
			return None
	@classmethod
	def get_health(cls):
		"""
		Retrieves the health status from the WellKnownApi and returns True if the health is 'ok', otherwise returns False.

		Returns:
		bool: True if the health status is 'ok', False otherwise.
		"""
		try:
			return WellKnownApi(cls.api_client).get_well_known_health_with_http_info().status_code == 200
		except:
			pass
		return False
