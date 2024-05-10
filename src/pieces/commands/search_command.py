from pieces_os_client.api.assets_api import AssetsApi
from pieces_os_client.api.search_api import SearchApi

from pieces.settings import Settings
from pieces.gui import show_error, print_asset_details
from pieces.assets.assets_api import AssetsCommandsApi


def search(query, **kwargs):
    search_type = kwargs.get('search_type', 'assets')

    # Join the list of strings into a single search phrase
    search_phrase = ' '.join(query)

    # Call the API function with the search phrase and type
    query = search_phrase
    
    # Determine the endpoint and perform the search based on the search type
    if search_type == 'assets':
        api_instance = AssetsApi(Settings.api_client)
        results = api_instance.assets_search_assets(query=query, transferables=False)
    elif search_type == 'ncs':
        api_instance = SearchApi(Settings.api_client)
        results = api_instance.neural_code_search(query=query)
    elif search_type == 'fts':
        api_instance = SearchApi(Settings.api_client)
        results = api_instance.full_text_search(query=query)
    else:
        show_error("Invalid search type", f"Search type '{search_type}' is not supported.")
        return

    # Check and extract asset IDs from the results
    if results:
        # Extract the iterable which contains the search results
        iterable_list = results.iterable if hasattr(results, 'iterable') else []

        # Check if iterable_list is a list and contains SearchedAsset objects
        if isinstance(iterable_list, list) and all(hasattr(asset, 'exact') and hasattr(asset, 'identifier') for asset in iterable_list):
            # Extracting suggested and exact IDs
            suggested_ids = [asset.identifier for asset in iterable_list if not asset.exact]
            exact_ids = [asset.identifier for asset in iterable_list if asset.exact]

            # Combine and store best and suggested matches in asset_ids
            combined_ids = exact_ids + suggested_ids

            # Prepare the combined list of names for printing
            combined_details = [(asset_id,  AssetsCommandsApi.get_asset_snapshot(asset_id).name) for asset_id in combined_ids]

            # Print the combined asset details
            if combined_details:
                print_asset_details(combined_details, "Asset Matches:", search_type)
            else:
                print("No matches found.")
        else:
            print("Unexpected response format or empty iterable.")
    else:
        print("No results found.")