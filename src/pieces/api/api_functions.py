## MAIN FUNCTION CALLS 
from typing import Dict,Union
from .config import *
import urllib.request
import json

def search_api(search_phrase, search_type):
    query = search_phrase
    
    # Determine the endpoint and perform the search based on the search type
    if search_type == 'assets':
        api_instance = pos_client.AssetsApi(api_client)
        response = api_instance.assets_search_assets(query=query, transferables=False)
    elif search_type == 'ncs':
        api_instance = pos_client.SearchApi(api_client)
        response = api_instance.neural_code_search(query=query)
    elif search_type == 'fts':
        api_instance = pos_client.SearchApi(api_client)
        response = api_instance.full_text_search(query=query)
    else:
        # Handle unknown search type
        raise ValueError("Unknown search type")

    # Return the response from the API
    return response


def get_models_ids() -> Dict[str, Dict[str, Union[str, int]]]:
    # api_instance = pos_client.ModelsApi(api_client)

    # api_response = api_instance.models_snapshot()
    # models = {model.name: {"uuid":model.id,"word_limit":model.max_tokens.input} for model in api_response.iterable if model.cloud or model.downloading} # getting the models that are available in the cloud or is downloaded
    

    
    # call the api until the sdks updated
    response = urllib.request.urlopen('http://localhost:1000/models').read()
    response = json.loads(response)["iterable"]
    models = {model["name"]:{"uuid":model["id"] ,"word_limit" :model["maxTokens"]["input"]} for model in response if model["cloud"] or model.get("downloaded",False)}
    return models


def sign_out():
    try:
        pos_client.OSApi(api_client).sign_out_of_os()
        return True
    except:
        return False