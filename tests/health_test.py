from pieces._vendor.pieces_os_client.wrapper.client import PiecesClient
from pieces.settings import Settings


def test_health():
    assert PiecesClient().is_pieces_running(8)
