## WELLNESS AND SYSTEM 
import platform
from pieces.gui import show_error
from pieces_os_client.models.application import Application
from pieces.store import *
from .config import *
import time
import subprocess
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


def open_pieces_os():
    try:
        pos_client.WellKnownApi(api_client).get_well_known_health()
    except: 
        pl = categorize_os()
        if pl == "WINDOWS":
            subprocess.Popen(["start", "os_server"], shell=True)
        elif pl == "LINUX":
            subprocess.Popen(["os_server"])
        elif pl == "MACOS":
            subprocess.Popen(["open", "os_server"])
        else:
            return False
        time.sleep(1) # wait for the server to open
    return True

def check_api(**kwargs):
    # Create an instance of the API class
    well_known_instance = pos_client.WellKnownApi(api_client)

    try:        
        # Make Sure Server is Running and Get Version
        version = well_known_instance.get_well_known_version()

        # Check if version is None or empty
        if not version:
            return False, "Server is not running", None

        # Decide if it's Windows, Mac, Linux or Web
        local_os = categorize_os()

        # Establish a local database connection
        conn = create_connection(applications_db_path)

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
    
def list_applications():
    applications_api = pos_client.ApplicationsApi(api_client)

    apps_raw = applications_api.applications_snapshot()
    
    return apps_raw

def register_application(existing_application=None):
    # Application
    applications_api = pos_client.ApplicationsApi(api_client)
    # application = Application(id="test", name="VS_CODE", version="1.9.1", platform="WINDOWS", onboarded=False, privacy="OPEN")
    application = existing_application

    try:
        api_response = applications_api.applications_register(application=application)
        
        return api_response
    except Exception as e:
        show_error("Exception when calling ApplicationsApi->applications_register:" , e)