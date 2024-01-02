import openapi_client
from openapi_client.rest import ApiException
from openapi_client.models.seeded_format import SeededFormat
from openapi_client.models.seeded_fragment import SeededFragment
from openapi_client.models.application import Application
from openapi_client.models.searched_assets import SearchedAssets
from store import create_connection, get_application, insert_application, create_table
from pprint import pprint
import platform

# Defining the host is optional and defaults to http://localhost:1000
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:1000"
)

# Initialize the ApiClient globally
api_client = openapi_client.ApiClient(configuration)

def categorize_os():
    # Get detailed platform information
    platform_info = platform.platform()

    # Categorize the platform information into one of the four categories
    if 'Windows' in platform_info:
        os_info = 'WINDOWS'
    elif 'Linux' in platform_info:
        os_info = 'LINUX'
    elif 'Darwin' in platform_info:  # Darwin is the base of macOS
        os_info = 'MACOS'
    else:
        os_info = 'WEB'  # Default to WEB if the OS doesn't match others

    return os_info

def search_api(search_phrase, search_type):
    query = search_phrase
    
    # # Initialize the API client
    # api_client = openapi_client.ApiClient(api_client)  # Replace with your actual API client initialization

    # Determine the endpoint and perform the search based on the search type
    if search_type == 'assets':
        api_instance = openapi_client.AssetsApi(api_client)
        response = api_instance.assets_search_assets(query=query, transferables=False)
    elif search_type == 'ncs':
        api_instance = openapi_client.SearchApi(api_client)
        response = api_instance.search_ncs(query=query)
    elif search_type == 'fts':
        api_instance = openapi_client.SearchApi(api_client)
        response = api_instance.search_fts(query=query)
    else:
        # Handle unknown search type
        raise ValueError("Unknown search type")

    # Return the response from the API
    return response

def check_api(**kwargs):
    # Create an instance of the API class
    well_known_instance = openapi_client.WellKnownApi(api_client)

    try:        
        # Make Sure Server is Running and Get Version
        version = well_known_instance.get_well_known_version()

        # Check if version is None or empty
        if not version:
            return False, "Server is not running", None

        # Decide if it's Windows, Mac, Linux or Web
        local_os = categorize_os()

        # Establish a local database connection
        conn = create_connection('applications.db')

        # Create the table if it does not exist
        create_table(conn)

        # Check the database for an existing application
        application_id = "DEFAULT"  # Replace with a default application ID
        application = get_application(conn, application_id)

        # If no application is found in the database, create and store a new one
        if application is None:
            application = Application(id=application_id, name="OPEN_SOURCE", version=version, platform=local_os, onboarded=False, privacy="OPEN")
            insert_application(conn, application)

        # Register the application
        registered_application = register_application(application)

        # Close the database connection
        conn.close()

        return True, version, registered_application

    except Exception as e:
        # Close the database connection in case of an exception
        if 'conn' in locals():
            conn.close()
        return False, "Exception when calling WellKnownApi->get_well_known_version: %s\n" % e



def get_asset_ids(max=None, **kwargs):
    assets_api = openapi_client.AssetsApi(api_client)

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
        print("Exception when calling AssetsApi->assets_identifiers_snapshot: %s\n" % e)
        return None
    
def get_asset_names(ids):
    names = []
    asset_api = openapi_client.AssetApi(api_client)

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
            print(f"Error occurred for ID {id}: {str(e)}")

    return names

def get_single_asset_name(id):
    
    asset_api = openapi_client.AssetApi(api_client)

    try:
        # Use the OpenAPI client to get asset snapshot
        api_response = asset_api.asset_snapshot(id)

        # Convert the response to a dictionary
        data = api_response.to_dict()

        # Extract the 'name' field and add it to the names list
        name = data.get('name')
        return name
    except ApiException as e:
        print(f"Error occurred for ID {id}: {str(e)}")

def get_asset_by_id(id):
    asset_api = openapi_client.AssetApi(api_client)

    try:
        # Use the OpenAPI client to get asset snapshot
        api_response = asset_api.asset_snapshot(id)

        # Convert the response to a dictionary
        data = api_response.to_dict()

        return data
    except ApiException as e:
        print(f"Error occurred for ID {id}: {str(e)}")
        return None
    
def create_new_asset(application, raw_string="testing", metadata=None):
    
    assets_api = openapi_client.AssetsApi(api_client)
    
    # Construct a Seed
    seed = openapi_client.Seed(
        asset=openapi_client.SeededAsset(
            application=application,
            format=openapi_client.SeededFormat(
                fragment=openapi_client.SeededFragment(
                    string=openapi_client.TransferableString(
                        raw=raw_string
                    )
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
        print("An exception occurred when calling AssetsApi->assets_create_new_asset: %s\n" % e)
        return None
    
def list_applications():
    applications_api = openapi_client.ApplicationsApi(api_client)

    apps_raw = applications_api.applications_snapshot()
    
    return apps_raw

def register_application(existing_application=None):
    # Application
    applications_api = openapi_client.ApplicationsApi(api_client)
    # application = Application(id="test", name="VS_CODE", version="1.9.1", platform="WINDOWS", onboarded=False, privacy="OPEN")
    application = existing_application

    try:
        api_response = applications_api.applications_register(application=application)
        
        return api_response
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_register: %s\n" % e)

def edit_asset_name(asset_id, new_name):
    asset_api = openapi_client.AssetApi(api_client)
    
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
        print(f"Error updating asset: {e}")

def update_asset(asset_id):
    asset_api = openapi_client.AssetApi(api_client)

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
        print(f"Error reading file: {e}")
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

    # Get the formats and update the raw string in each format
    formats = working_asset.get('formats', {}).get('iterable', [])
    for format in formats:
        string_obj = format.get('fragment', {}).get('string', {})
        if 'raw' in string_obj:
            string_obj['raw'] = new_content

    # Update all string occurrences within the asset
    update_string(working_asset)  # Uncomment this line to enable updating

    # Update the asset using the API
    try:
        response = asset_api.asset_update(asset=working_asset, transferables=False)
        # print(response)
        print("Asset updated successfully.")
    except Exception as e:
        print(f"Error updating asset: {e}")

def delete_asset_by_id(asset_id):
    delete_instance = openapi_client.AssetsApi(api_client)
    
    try:
        response = delete_instance.assets_delete_asset(asset_id)
        return response
    except Exception as e:
        return f"Failed to delete {asset_id}"