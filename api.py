import requests
import pprint

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