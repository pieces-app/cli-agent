from pieces.settings import Settings


def sign_out(**kwargs):
    try:
        Settings.pieces_client.user.logout()
    except:
        pass


def sign_in(**kwargs):
    try:
        Settings.pieces_client.user.login()
    except:
        pass
