import openapi_client
from openapi_client.rest import ApiException
from openapi_client.models.application import Application
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

# API CALLS
def check_api(**kwargs):
    # Create an instance of the API class
    well_known_instance = openapi_client.WellKnownApi(api_client)

    try:        
        # Make Sure Server is Running and Get Version
        version = well_known_instance.get_well_known_version()
        
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

def get_asset_details(id):
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
    # Assuming there is an OpenAPI generated client for the Assets API
    assets_api = openapi_client.AssetsApi(api_client)
    
    # Constructing the Seed object similar to the Dart example
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
        type=openapi_client.SeedTypeEnum.ASSET
    )
    
    # Creating the new asset using the assets API
    try:
        created_asset = assets_api.assets_create_new_asset(seed)
        return created_asset
    except ApiException as e:
        print("An exception occurred when calling AssetsApi->assets_create_new_asset: %s\n" % e)
        return None
    
def register_application(existing_application=None):
    # Application
    applications_api = openapi_client.ApplicationsApi(api_client)
    # application = Application(id="test", name="VS_CODE", version="1.9.1", platform="WINDOWS", onboarded=False, privacy="OPEN")
    application = existing_application

    try:
        # /applications/register [POST]
        api_response = applications_api.applications_register(application=application)
        # print("The response of ApplicationsApi->applications_register:\n")
        return api_response
        # pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_register: %s\n" % e)