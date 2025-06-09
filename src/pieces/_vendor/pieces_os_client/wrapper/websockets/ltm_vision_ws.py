from .base_websocket import BaseWebsocket


from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import PiecesClient
    import websocket
    from pieces._vendor.pieces_os_client.models.workstream_pattern_engine_status import (
        WorkstreamPatternEngineStatus,
    )


class LTMVisionWS(BaseWebsocket):
    def __init__(
        self,
        pieces_client: "PiecesClient",
        on_message_callback: Callable[[str], None],
        on_open_callback: Optional[
            Callable[["websocket.WebSocketApp"], "WorkstreamPatternEngineStatus"]
        ] = None,
        on_error: Optional[
            Callable[["websocket.WebSocketApp", Exception], None]
        ] = None,
        on_close: Optional[Callable[["websocket.WebSocketApp", str, str], None]] = None,
    ):
        super().__init__(
            pieces_client, on_message_callback, on_open_callback, on_error, on_close
        )

    @property
    def url(self):
        return self.pieces_client.LTM_VISION_WS_URL

    def on_message(self, ws, _):
        message = self.pieces_client.work_stream_pattern_engine_api.workstream_pattern_engine_processors_vision_status()
        self.pieces_client.copilot.context.ltm.ltm_status = message
        self.on_message_callback(message)
