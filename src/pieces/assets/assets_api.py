from pieces.settings import Settings
from pieces.gui import show_error
from pieces_os_client.rest import ApiException
from typing import Dict,List
import json

from pieces_os_client.api.assets_api import AssetsApi
from pieces_os_client.api.asset_api import AssetApi
from pieces_os_client.api.format_api import FormatApi

from pieces_os_client.models.seed import Seed
from pieces_os_client.models.seeded_asset import SeededAsset
from pieces_os_client.models.seeded_format import SeededFormat
from pieces_os_client.models.seeded_fragment import SeededFragment
from pieces_os_client.models.transferable_string import TransferableString
from pieces_os_client.models.classification_generic_enum import ClassificationGenericEnum
from pieces_os_client.models.asset_reclassification import AssetReclassification


class AssetsCommandsApi:
	@staticmethod
	def create_new_asset(raw_string, metadata=None):
		assets_api = AssetsApi(Settings.api_client)

		# Construct a Seed
		seed = Seed(
			asset=SeededAsset(
				application=Settings.application,
				format=SeededFormat(
					fragment=SeededFragment(
						string=TransferableString(raw=raw_string)
					)
				),
				metadata=metadata  # This should be constructed as per the SDK's definition
			),
			type="SEEDED_ASSET"
		)
		
		# Creating the new asset using the assets API
		created_asset = assets_api.assets_create_new_asset(transferables=False, seed=seed)
		return created_asset
	
	@classmethod
	def get_asset_ids(max=None, **kwargs):
		assets_api = AssetsApi(Settings.api_client)
		# Call the API to get assets identifiers
		api_response = assets_api.assets_identifiers_snapshot()

		# Extract data from the response
		data = api_response.to_dict()  # Convert the response to a dictionary

		# Extract the 'id' values from each item in the 'iterable' list
		ids = [item['id'] for item in data.get('iterable', [])]

		# If max is specified, return only up to max ids
		if max is not None and max > 0:
			return ids[:max]

		# Return the list of ids
		return ids
	
	@classmethod
	def get_assets_info_list(cls,max_assets=10) -> List[Dict[str,str]]:
		"""
		Returns a list of dictionaries containing the name and id of each asset
		"""

		assets = []
		asset_api = AssetApi(Settings.api_client)


		ids = cls.get_asset_ids()
		for id in ids[:max_assets]:
			# Use the OpenAPI client to get asset snapshot
			api_response = asset_api.asset_snapshot(id)

			# Convert the response to a dictionary
			data = api_response.to_dict()

			# Extract the 'name' field and add it to the names list
			name = data.get('name',"New asset")

			# Add the name to the dictionary
			asset = {}
			asset["name"] = name

			asset["id"] = id

			assets.append(asset)
				
		return assets

	@staticmethod
	def get_single_asset_name(id):
		asset_api = AssetApi(Settings.api_client)

		try:
			# Use the OpenAPI client to get asset snapshot
			api_response = asset_api.asset_snapshot(id)

			# Convert the response to a dictionary
			data = api_response.to_dict()

			# Extract the 'name' field and add it to the names list
			name = data.get('name')
			return name
		except ApiException as e:
			show_error(f"Error occurred for ID {id}: ",str(e))

	def get_asset_by_id(id):
		asset_api = AssetApi(Settings.api_client)
		
		# Use the OpenAPI client to get asset snapshot
		api_response = asset_api.asset_snapshot(id)

		# Convert the response to a dictionary
		data = api_response.to_dict()

		return data
	@classmethod
	def edit_asset_name(cls,asset_id, new_name):
		asset_api = AssetApi(Settings.api_client)

		# Get the asset using the provided asset_id
		asset = cls.get_asset_by_id(asset_id)

		# Check if the existing name is found and update it
		existing_name = asset.get('name', 'Existing name not found')
		if existing_name != 'Existing name not found':
			asset['name'] = new_name
			print(f"Asset name changed from '{existing_name}' to '{new_name}'")
		else:
			print(existing_name)
			return

		# Update the asset using the API
		try:
			asset_api.asset_update(asset=asset, transferables=False)
			print("Asset name updated successfully.")
		except Exception as e:
			show_error("Error updating asset: ",{e})

	def delete_asset_by_id(asset_id):
		delete_instance = AssetsApi(Settings.api_client)

		try:
			response = delete_instance.assets_delete_asset(asset_id)
			return response
		except Exception as e:
			return f"Failed to delete {asset_id}"

	@staticmethod
	def reclassify_asset(asset_id, classification):
		asset_api = AssetApi(Settings.api_client)
		with open(Settings.extensions_dir) as f:
			extension_mapping = json.load(f)
			if classification not in extension_mapping:
				show_error(f"Invalid classification: {classification}","Please choose from the following: \n "+", ".join(extension_mapping.keys()))
				return
			
		try:
			asset = asset_api.asset_snapshot(asset_id)
			if asset.original.reference.classification.generic == ClassificationGenericEnum.IMAGE:
				show_error("Error in reclassify asset","Original format is not supported")
				return
			asset_api.asset_reclassify(asset_reclassification=AssetReclassification(ext=classification,asset=asset),
												transferables=False)
			print(f"reclassify {asset.name} the asset to {classification} successfully")
		except Exception as e:
			show_error("Error reclassifying asset: ",{e})

	@staticmethod
	def update_asset_value(file_path,asset_id):
		try:
			with open(file_path,"r") as f:
				data = f.read()
		except FileNotFoundError:
			show_error("Error in update asset","File not found")
			return
		asset_api = AssetApi(Settings.api_client)
		format_api = FormatApi(Settings.api_client)

		# get asset
		created = asset_api.asset_snapshot(asset_id, transferables=False)

		# update the original format's value
		original = format_api.format_snapshot(created.original.id, transferable=True)
		if original.classification.generic == ClassificationGenericEnum.IMAGE:
			show_error("Error in update asset","Original format is not supported")
			return
		if original.fragment.string.raw:
			original.fragment.string.raw = data
		elif original.file.string.raw:
			original.file.string.raw = data
		# check if the string value is not empty
		else :
			show_error("Error in update asset","Original value is empty")
			return

		format_api.format_update_value(transferable=False, format=original)

		print(f"{created.name} updated successfully.")

	def extract_asset_info(data:dict) -> dict:
		"""
		Return some info about the asset
		:param data: The data containing information about the asset
		:return: A dictionary containing the asset's name, date created, date updated, type, language, and raw code snippet
		"""

		name = data.get('name', 'Unknown')
		created_readable = data.get('created', {}).get('readable', 'Unknown')
		updated_readable = data.get('updated', {}).get('readable', 'Unknown')
		type = "No Type"
		language = "No Language"
		raw = None  # Initialize raw code snippet as None
		formats = data.get('formats', {})

		if formats:
			iterable = formats.get('iterable', [])
			if iterable:
				first_item = iterable[0] if len(iterable) > 0 else None
				if first_item:
					classification_str = first_item.get('classification', {}).get('generic')
					if classification_str:
						# Extract the last part after the dot
						type = classification_str.split('.')[-1]

					language_str = first_item.get('classification', {}).get('specific')
					if language_str:
						# Extract the last part after the dot
						language = language_str.split('.')[-1]

					fragment_string = first_item.get('fragment', {}).get('string').get('raw')
					if fragment_string:
						raw = fragment_string

		return {"name":name,
				"created_at":created_readable,
				'updated_at': updated_readable,
				"type" :type,
				"language": language,
				"raw": raw}

