import openapi_client
from openapi_client.rest import ApiException
from openapi_client.models.seeded_format import SeededFormat
from openapi_client.models.seeded_fragment import SeededFragment
from openapi_client.models.application import Application
from openapi_client.models.searched_assets import SearchedAssets 
from openapi_client.models.models import Models
# from store import create_connection, get_application, insert_application, create_table
from store import *
from openapi_client.models.qgpt_stream_input import QGPTStreamInput
from openapi_client.models.qgpt_question_input import QGPTQuestionInput
from openapi_client.models.qgpt_stream_output import QGPTStreamOutput
from openapi_client.models.relevant_qgpt_seed import RelevantQGPTSeed
from openapi_client.models.relevant_qgpt_seeds import RelevantQGPTSeeds
from openapi_client.models.format import Format
from openapi_client.models.seed import Seed
from openapi_client.models.exported_asset import ExportedAsset
from openapi_client.models.grouped_timestamp import GroupedTimestamp
from openapi_client.models.file_format import FileFormat
from openapi_client.models.classification import Classification
from pprint import pprint
import platform
import json
import websocket
import threading
import time
from datetime import datetime

#Globals
response_received = None
existing_model_id = ""
query = ""
ws = websocket
loading = False
last_message_time = None
initial_timeout = 10  # seconds
subsequent_timeout = 3  # seconds
first_token_received = False



# Defining the host is optional and defaults to http://localhost:1000
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:1000"
)

# Initialize the ApiClient globally
api_client = openapi_client.ApiClient(configuration)

def on_message(ws, message):
    global last_message_time, first_token_received
    last_message_time = time.time()
    first_token_received = True
    
    try:
        response = json.loads(message)
        answers = response.get('question', {}).get('answers', {}).get('iterable', [])
        for answer in answers:
            text = answer.get('text')
            if text:
                print(text, end='')

        # Check if the response is complete and add a newline
        status = response.get('status', '')
        if status == 'COMPLETED':
            print("\n")  # Add a newline after the complete response
            loading = False

    except Exception as e:
        print(f"Error processing message: {e}")

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Closed")
    print()
    # print(f"WebSocket closed, Close status code: {close_status_code}, Message: {close_msg}")

def on_open(ws):
    # global existing_model_id
    print("WebSocket connection opened.")
    print()
    send_message(ws=ws)  # Send a test message upon connection
    
def start_websocket_connection():
    print("Starting WebSocket connection...")
    ws_app = websocket.WebSocketApp("ws://localhost:1000/qgpt/stream",
                                    on_open=on_open,
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)

    return ws_app

def start_ws():
    global ws
    
    if ws is None:
        print()
        print("No WebSocket provided, opening a new connection.")
        ws = start_websocket_connection()
    else:
        print("Using provided WebSocket connection.")
    print(f"Type of ws before sending message: {type(ws)}")  # Debug print
    ws.run_forever()  # Start the WebSocket connection
    send_message(ws=ws)

# def send_message(ws):
#     global existing_model_id
#     global this_query

#     # Construct the message in the format expected by the server
#     message = {
#         "question": {
#             "query": this_query,
#             "relevant": {"iterable": []},
#             "model": existing_model_id
#         }
#     }

#     # Convert the message to a JSON string
#     json_message = json.dumps(message)

#     # Send the JSON message through the WebSocket
#     ws.send(json_message)
#     # print(f"Sent message to server: {json_message}")
#     print()
#     print("Response: ")

def send_message(ws):
    global existing_model_id, this_query

    # Construct the message in the format expected by the server
    message = {
        "question": {
            "query": this_query,
            "relevant": {"iterable": []},
            "model": existing_model_id
        }
    }

    # Convert the message to a JSON string
    json_message = json.dumps(message)

    # Check if the WebSocket is still open before sending the message
    if ws and ws.sock and ws.sock.connected:
        try:
            # Send the JSON message through the WebSocket
            ws.send(json_message)
            print("Response: ")
        except Exception as e:
            print(f"Error sending message: {e}")
    else:
        pass
        # print("WebSocket connection is not open, unable to send message.")


def close_websocket_connection(ws):
    if ws:
        print("Closing WebSocket connection...")
        ws.close()

# def ask_question(model_id, query):
#     global response_received, existing_model_id, this_query, ws, last_message_time, first_token_received

#     existing_model_id = model_id
#     this_query = query

#     def start_ws(ws):
#         if ws is None:
#             print("No WebSocket provided, opening a new connection.")
#             ws = start_websocket_connection()
#         else:
#             print("Using provided WebSocket connection.")
        
#         # print(f"Type of ws before sending message: {type(ws)}")
#         ws.run_forever()
#         send_message(ws=ws)

#     ws = None
#     # ws_thread = threading.Thread(target=start_ws, args=(ws,))
#     # ws_thread.start()
#     ws_thread = threading.Thread(target=start_ws)
#     ws_thread.start()
        
def ask_question(model_id, query, ws=None):
    global response_received, existing_model_id, this_query, last_message_time, first_token_received

    existing_model_id = model_id
    this_query = query

    def start_ws():
        nonlocal ws
        if ws is None or not ws.sock or not ws.sock.connected:
            print()
            print("No WebSocket provided or connection is closed, opening a new connection.")
            ws = start_websocket_connection()
        else:
            print("Using provided WebSocket connection.")
        
        ws.run_forever()
        send_message(ws=ws)

    if ws is None or not ws.sock or not ws.sock.connected:
        ws_thread = threading.Thread(target=start_ws)
        ws_thread.start()
    else:
        send_message(ws=ws)  # If ws is already connected, just send the message

    # print("Waiting for response...")
    last_message_time = time.time()

    while response_received is None:
        current_time = time.time()
        if first_token_received:
            if current_time - last_message_time > subsequent_timeout:
                break
        else:
            if current_time - last_message_time > initial_timeout:
                break
        time.sleep(0.1)

    return ws, ws_thread if 'ws_thread' in locals() else None

# def ask_question(model_id, query):
#     global response_received, existing_model_id, this_query, last_message_time, first_token_received

#     existing_model_id = model_id
#     this_query = query
#     ws = None  # Define ws here

#     def start_ws():
#         nonlocal ws  # Use the non-local ws variable
#         if ws is None:
#             print("No WebSocket provided, opening a new connection.")
#             ws = start_websocket_connection()
#         else:
#             print("Using provided WebSocket connection.")

#         ws.run_forever()
#         send_message(ws=ws)

#     ws_thread = threading.Thread(target=start_ws)
#     ws_thread.start()

#     print("Waiting for response...")
#     timeout = 7  # seconds
#     last_message_time = time.time()  # Initialize last message time

#     while response_received is None:
#         current_time = time.time()
#         if first_token_received:
#             # Subsequent timeout check
#             if current_time - last_message_time > subsequent_timeout:
#                 break
#         else:
#             # Initial timeout check
#             if current_time - last_message_time > initial_timeout:
#                 break
#         time.sleep(0.1)  # Sleep briefly to yield execution

#     return ws, ws_thread

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



# def ask_question(model_id, query="This is a test"):
#     global response_received

#     def start_ws():
#         ws = start_websocket_connection()
#         send_message(ws, query=query)

#     # Start WebSocket in a new thread
#     ws_thread = threading.Thread(target=start_ws)
#     ws_thread.start()

#     # Wait for the response (with a timeout to prevent infinite waiting)
#     timeout = 60  # seconds
#     start_time = time.time()
#     while response_received is None and (time.time() - start_time) < timeout:
#         time.sleep(0.1)  # Sleep briefly to yield execution

#     if response_received is not None:
#         print("Response:", response_received)
#     else:
#         print("No response received within the timeout period.")


     ## QGPTStreamInput
    ## You can either pass in relevance or question
    ## QGPTQuestionInput requires a model id and query
    ## When running, the error message indicates that you MUST pass in relevant
    ## Pass in the query, model and RelevantQGPTSeeds
    ## RelevantQGPTSeeds has iterable which is a list of RelevantQGPTSeed

    ## Try creating a blank seed
    # demo_seed = RelevantQGPTSeed()

    # ## Add the seed to a list
    # iterable = [demo_seed]

    # ## Create Instance
    # api_instance = openapi_client.QGPTApi(api_client)
    
    # ## Create the stream input
    # qgpt_stream_input = QGPTStreamInput(
    #     question=QGPTQuestionInput(
    #         query=query, model=model_id, relevant=RelevantQGPTSeeds(iterable=iterable)
    #         ))

    # response = api_instance.qgpt_stream(qgpt_stream_input=qgpt_stream_input)
    
 
    
    

def list_models():
    
    models_api = openapi_client.ModelsApi(api_client)

    response = models_api.models_snapshot()
    return response

def search_api(search_phrase, search_type):
    query = search_phrase
    
    # Determine the endpoint and perform the search based on the search type
    if search_type == 'assets':
        api_instance = openapi_client.AssetsApi(api_client)
        response = api_instance.assets_search_assets(query=query, transferables=False)
    elif search_type == 'ncs':
        api_instance = openapi_client.SearchApi(api_client)
        response = api_instance.neural_code_search(query=query)
    elif search_type == 'fts':
        # print(query)
        api_instance = openapi_client.SearchApi(api_client)
        response = api_instance.full_text_search(query=query)
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
        # create_tables(conn)

        # Check the database for an existing application
        application_id = "DEFAULT"  # Replace with a default application ID
        application = get_application(conn, application_id)
        # application =  get_application_with_versions(conn, application_id)

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
    
def create_new_asset(application, raw_string, metadata=None):
    
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

def update_asset(asset_id, application):
    ## NOT CURRENTLY WORKING ##
    
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

    # print(working_asset)

    

    # exported_asset = ExportedAsset(name="This is a test", description="Testing description", raw=FileFormat(string={"string": "This, This is me testing export asset"}), created=GroupedTimestamp(value=datetime.now()))

    # print(exported_asset)
    format_api_instance = openapi_client.FormatApi(api_client)
    format = openapi_client.Format(asset=working_asset, id=asset_id, creator="ea47fe2f-a503-4edb-861a-7c55ca446859", classification=Classification(generic="CODE",specific="tex"), role="BOTH", application=application),
    api_response = format_api_instance.format_update_value(transferable=False, format=format)
    print(api_response)

    ## Update the format's value that lives on the asset
    ## Requires format update. Get format from asset we want to update (from the actual asset)
    ## Update value locally. Send through api. 
    ## Optional: Need assets stream running
    ## Once we get a 200, refetch asset or replace locally
    ## One option is to run in background for speed
    ## Lister on conversations and assets
    ## 


    # # Get the formats and update the raw string in each format
    # formats = working_asset.get('formats', {}).get('iterable', [])
    # for format in formats:
    #     string_obj = format.get('fragment', {}).get('string', {})
    #     if 'raw' in string_obj:
    #         string_obj['raw'] = new_content

    # # # Update all string occurrences within the asset
    # # update_string(working_asset)  # Uncomment this line to enable updating

    # # # Update the asset using the API
    # # try:
    # #     response = asset_api.asset_update(asset=working_asset, transferables=False)
    # #     # print(response)
    # #     print("Asset updated successfully.")
    # except Exception as e:
    #     print(f"Error updating asset: {e}")

def delete_asset_by_id(asset_id):
    delete_instance = openapi_client.AssetsApi(api_client)
    
    try:
        response = delete_instance.assets_delete_asset(asset_id)
        return response
    except Exception as e:
        return f"Failed to delete {asset_id}"