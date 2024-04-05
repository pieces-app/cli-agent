## ASSET CALLS 
from .config import *
from pieces.gui import show_error
from pydantic import ValidationError
from pieces_os_client.models.classification import Classification
from pieces_os_client.rest import ApiException
from typing import Dict,List
import json

def create_new_asset(application, raw_string, metadata=None):
    assets_api = pos_client.AssetsApi(api_client)

    # Construct a Seed
    seed = pos_client.Seed(
        asset=pos_client.SeededAsset(
            application=application,
            format=pos_client.SeededFormat(
                fragment=pos_client.SeededFragment(
                    string=pos_client.TransferableString(raw=raw_string)
                )
            ),
            metadata=metadata  # This should be constructed as per the SDK's definition
        ),
        type="SEEDED_ASSET"
    )
    
    # Creating the new asset using the assets API
    try:
        created_asset = assets_api.assets_create_new_asset(transferables=False, seed=seed)
        return created_asset
    except ApiException as e:
        show_error("An exception occurred when calling AssetsApi->assets_create_new_asset:" , e)
        return None

def get_asset_ids(max=None, **kwargs):
    assets_api = pos_client.AssetsApi(api_client)

    try:
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
    except ApiException as e:
        # Handle the API exception
        show_error("Exception when calling AssetsApi->assets_identifiers_snapshot:" ,e)
        return None
    
def get_assets_info_list() -> List[Dict[str,str]]:
    """
    Returns a list of dictionaries containing the name and id of each asset
    """

    assets = []
    asset_api = pos_client.AssetApi(api_client)


    ids = get_asset_ids()
    for id in ids:
        try:
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
            
        except ApiException as e:
            show_error(f"Error occurred for ID {id}:", str(e))
            
    return assets


def get_single_asset_name(id):
    asset_api = pos_client.AssetApi(api_client)

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
    asset_api = pos_client.AssetApi(api_client)

    try:
        # Use the OpenAPI client to get asset snapshot
        api_response = asset_api.asset_snapshot(id)

        # Convert the response to a dictionary
        data = api_response.to_dict()

        return data
    except ApiException as e:
        show_error(f"Error occurred for ID {id}:" ,str(e))
        return None
    except ValidationError as e:
        show_error(f"Parsing error in asset with ID {id}:", str(e))

def edit_asset_name(asset_id, new_name):
    asset_api = pos_client.AssetApi(api_client)

    # Get the asset using the provided asset_id
    asset = get_asset_by_id(asset_id)

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
        response = asset_api.asset_update(asset=asset, transferables=False)
        print("Asset name updated successfully.")
    except Exception as e:
        show_error("Error updating asset: ",{e})

def delete_asset_by_id(asset_id):
    delete_instance = pos_client.AssetsApi(api_client)

    try:
        response = delete_instance.assets_delete_asset(asset_id)
        return response
    except Exception as e:
        return f"Failed to delete {asset_id}"


def reclassify_asset(asset_id, classification):
    asset_api = pos_client.AssetApi(api_client)
    with open(extensions_dir) as f:
        extension_mapping = json.load(f)
        if classification not in extension_mapping:
            show_error(f"Invalid classification: {classification}","Please choose from the following: \n "+", ".join(extension_mapping.keys()))
            return
        
    try:
        asset = asset_api.asset_snapshot(asset_id)
        if asset.original.reference.classification.generic != pos_client.ClassificationGenericEnum.IMAGE:
            show_error("Error in reclassify asset","Original format is not supported")
            return
        asset_api.asset_reclassify(asset_reclassification=pos_client.AssetReclassification(ext=classification,asset=asset),
                                              transferables=False)
        print(f"reclassify {asset.name} the asset to {classification} successfully")
    except Exception as e:
        show_error("Error reclassifying asset: ",{e})


def update_asset_value(file_path,asset_id):
    try:
        with open(file_path,"r") as f:
            data = f.read()
    except FileNotFoundError:
        show_error("Error in update asset","File not found")
        return
    asset_api = pos_client.AssetApi(api_client)
    format_api = pos_client.FormatApi(api_client)

    # get asset
    created = asset_api.asset_snapshot(asset_id, transferables=False)

    # update the original format's value
    original = format_api.format_snapshot(created.original.id, transferable=True)
    if original.classification.generic != pos_client.ClassificationGenericEnum.IMAGE:
        show_error("Error in update asset","Original format is not supported")
        return
    original_value = original.fragment.string.raw if original.fragment and original.fragment.string else None

    # check if the string value is not empty
    if original_value is None:
        show_error("Error in update asset","Original value is empty")
        return

    # call our endpoint to update our value. && update our value.
    original.fragment.string.raw = data
    format_api.format_update_value(transferable=False, format=original)


