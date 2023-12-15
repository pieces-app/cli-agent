import requests
import pprint
import json

def check_api(**kwargs):
    # Logic to check the API
    try:
        response = requests.get('http://localhost:1000/.well-known/version')
        response.raise_for_status()
        
        # Return True and the response text if successful
        return True, response.text
    except requests.RequestException as e:
        # Return False and the error message if there's an exception
        return False, str(e)
    
def get_asset_ids(max=None, **kwargs):
    # Logic to check the API
    try:
        response = requests.get('http://localhost:1000/assets/identifiers')
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Extract the 'id' values from each item in the 'iterable' list
        ids = [item['id'] for item in data.get('iterable', [])]

        # If max is specified, return only up to max ids
        if max is not None and max > 0:
            return ids[:max]

        # Return the list of ids
        return ids
    except requests.RequestException as e:
        # Return the error message if there's an exception
        return str(e)
    
def get_asset_names(ids):
    names = []
    # print(ids[0]["id"])

    # Iterate over each ID and make a request to the endpoint
    for id in ids:
        try:
            response = requests.get(f'http://localhost:1000/asset/{id}')
            response.raise_for_status()

            # Parse the JSON response
            data = response.json()

            # Extract the 'name' field and add it to the names list
            name = data.get('name')
            if name:
                names.append(name)
        except requests.RequestException as e:
            print(f"Error occurred for ID {id}: {str(e)}")

    return names

def get_asset_details(id):
    # names = []
    # print(ids[0]["id"])

    # Iterate over each ID and make a request to the endpoint
    try:
        response = requests.get(f'http://localhost:1000/asset/{id}')
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Extract the 'name' field and add it to the names list
        # name = data.get('name')
        # if name:
        #     names.append(name)
        return data
    except requests.RequestException as e:
        print(f"Error occurred for ID {id}: {str(e)}")

    # return names
