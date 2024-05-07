from pieces_os_client.api.os_api import OSApi
from pieces.settings import Settings

def sign_out():
    try:
        OSApi(Settings.api_client).sign_out_of_os()
        return True
    except:
        return False