## WELLNESS AND SYSTEM 
import platform
from .config import *
import time
import subprocess
from pieces import __version__
from typing import Optional 
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
def get_version() -> Optional[str]:
    """Get pieces os version return None if there is a problem"""
    try:
        version = pos_client.WellKnownApi(api_client).get_well_known_version()
        return version
    except: # There is a problem in the startup
        return None
def open_pieces_os() -> Optional[str]:
    """Open pieces os and return its version"""
    version = get_version()
    if version:
        return version
    else:
        pl = categorize_os()
        if pl == "WINDOWS":
            subprocess.Popen(["start", "os_server"], shell=True)
        elif pl == "LINUX":
            subprocess.Popen(["os_server"])
        elif pl == "MACOS":
            subprocess.Popen(["open", "os_server"])
        time.sleep(2) # wait for the server to open
        
        return get_version() # pieces os version

def connect_api() -> pos_client.Application:
    # Decide if it's Windows, Mac, Linux or Web
    local_os = categorize_os()


    api_instance = pos_client.ConnectorApi(api_client)
    seeded_connector_connection = pos_client.SeededConnectorConnection(
        application=pos_client.SeededTrackedApplication(
            name = pos_client.ApplicationNameEnum.OPEN_SOURCE,
            platform = local_os,
            version = __version__))
    api_response = api_instance.connect(seeded_connector_connection=seeded_connector_connection)
    return api_response.application
    

def list_applications():
    applications_api = pos_client.ApplicationsApi(api_client)

    apps_raw = applications_api.applications_snapshot()
    
    return apps_raw