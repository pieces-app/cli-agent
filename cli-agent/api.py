import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:1000
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:1000"
)

# Initialize the ApiClient globally
api_client = openapi_client.ApiClient(configuration)

# API CALLS
def check_api(**kwargs):
    
    well_known_instance = openapi_client.WellKnownApi(api_client)

    try:
        # /.well-known/version [Get]
        api_response = well_known_instance.get_well_known_version()
        return True, api_response
    except Exception as e:
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
    
