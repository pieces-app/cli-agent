import pieces_os_client as pos_client
from pieces.settings import Settings

def search_api(search_phrase, search_type):
    query = search_phrase
    
    # Determine the endpoint and perform the search based on the search type
    if search_type == 'assets':
        api_instance = pos_client.AssetsApi(Settings.api_client)
        response = api_instance.assets_search_assets(query=query, transferables=False)
    elif search_type == 'ncs':
        api_instance = pos_client.SearchApi(Settings.api_client)
        response = api_instance.neural_code_search(query=query)
    elif search_type == 'fts':
        api_instance = pos_client.SearchApi(Settings.api_client)
        response = api_instance.full_text_search(query=query)
    else:
        # Handle unknown search type
        raise ValueError("Unknown search type")

    # Return the response from the API
    return response




def sign_out():
    try:
        pos_client.OSApi(Settings.api_client).sign_out_of_os()
        return True
    except:
        return False