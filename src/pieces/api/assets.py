## ASSET CALLS 
from .config import *
from pieces.gui import show_error
from pydantic import ValidationError
from pieces_os_client.models.classification import Classification
from pieces_os_client.rest import ApiException
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
    
def get_asset_names(ids):
    names = []
    asset_api = pos_client.AssetApi(api_client)

    for id in ids:
        try:
            # Use the OpenAPI client to get asset snapshot
            api_response = asset_api.asset_snapshot(id)

            # Convert the response to a dictionary
            data = api_response.to_dict()

            # Extract the 'name' field and add it to the names list
            name = data.get('name')
            if name:
                names.append(name)
        except ApiException as e:
            show_error(f"Error occurred for ID {id}:", str(e))

    return names


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

    # Print the entire asset with updates
    print("Asset with updates, ready to send to API:\n", asset)

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

def update_asset(asset_id, application):
    ## NOT CURRENTLY WORKING ##

    asset_api = pos_client.AssetApi(api_client)

    working_asset = get_asset_by_id(asset_id)
    # file_name = working_asset.get('name')
    file_name = "Pieces_is_the_Best.tex" ################ TEST

    # Define the path to the file
    file_path = f"opened_snippets/{file_name}"

    # Open and read the file content
    try:
        with open(file_path, 'r') as file:
            new_content = file.read()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return
    except Exception as e:
        show_error("Error reading file: ",{e})
        return

    def update_string(obj):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if isinstance(value, dict):
                    update_string(value)
                elif isinstance(value, list):
                    for item in value:
                        update_string(item)
                elif key == 'raw' and isinstance(value, str):
                    obj[key] = new_content

    # print(working_asset)
    # exported_asset = ExportedAsset(name="This is a test", description="Testing description", raw=FileFormat(string={"string": "This, This is me testing export asset"}), created=GroupedTimestamp(value=datetime.now()))

    # print(exported_asset)
    format_api_instance = pos_client.FormatApi(api_client)
    format = (
        pos_client.Format(
            asset=working_asset,
            id=asset_id,
            creator="ea47fe2f-a503-4edb-861a-7c55ca446859",
            classification=Classification(generic="CODE", specific="tex"),
            role="BOTH",
            application=application,
        ),
    )
    api_response = format_api_instance.format_update_value(
        transferable=False, format=format
    )
    print(api_response)