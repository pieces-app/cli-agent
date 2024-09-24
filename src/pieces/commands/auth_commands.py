from pieces.settings import Settings

def sign_out():
    try:
        Settings.pieces_client.user.logout()
    except:
        pass

def sign_in():
    try:
        Settings.pieces_client.user.login()
    except:
        pass