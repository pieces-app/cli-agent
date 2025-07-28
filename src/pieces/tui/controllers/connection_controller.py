"""Controller for handling connection state and health checks."""

from pieces.settings import Settings
from .base_controller import BaseController, EventType
from pieces._vendor.pieces_os_client.wrapper.websockets.health_ws import HealthWS


class ConnectionController(BaseController):
    """Handles connection state monitoring and health checks."""

    def __init__(self):
        """Initialize the connection controller."""
        super().__init__()
        self._is_connected = False

    def initialize(self):
        """Start monitoring connection health."""
        if self._initialized:
            return
        self._initialized = True
        self._health_websocket = HealthWS.get_instance() or HealthWS(
            pieces_client=Settings.pieces_client,
            on_message_callback=self._check_connection,
        )

    def cleanup(self):
        """Stop monitoring connection health."""
        # Stop health check thread
        if self._health_websocket:
            self._health_websocket.close()
            self._health_websocket = None

        self._initialized = False

    def _check_connection(self, health_message: str):
        """Check if Pieces OS is connected and healthy."""
        try:
            health = health_message.lower() == "ok"

            if health and not self._is_connected:
                self._is_connected = True
                self.emit(
                    EventType.CONNECTION_ESTABLISHED,
                    {"health": health, "version": Settings.pieces_os_version},
                )

            elif not health and self._is_connected:
                # Connection lost
                self._is_connected = False
                self.emit(EventType.CONNECTION_LOST, None)

        except Exception as e:
            if self._is_connected:
                self._is_connected = False
                self.emit(EventType.CONNECTION_LOST, {"error": str(e)})

    def is_connected(self) -> bool:
        """Check if currently connected."""
        return self._is_connected

    def reconnect(self):
        """Attempt to reconnect to Pieces OS."""
        if self._health_websocket:
            self._health_websocket.reconnect()
        else:
            self._health_websocket = HealthWS.get_instance() or HealthWS(
                pieces_client=Settings.pieces_client,
                on_message_callback=self._check_connection,
            )
            self.reconnect()
        self.emit(EventType.CONNECTION_RECONNECTING, None)
