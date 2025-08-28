"""Controller for handling connection state and health checks."""

import time
from pieces.settings import Settings
from .base_controller import BaseController, EventType
from pieces._vendor.pieces_os_client.wrapper.websockets.health_ws import HealthWS


class ConnectionController(BaseController):
    """Handles connection state monitoring and health checks."""

    def __init__(self):
        """Initialize the connection controller."""
        super().__init__()
        self._is_connected = False
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        self._last_reconnect_time = 0
        self._base_reconnect_delay = 5

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
        try:
            # Stop health check thread
            if self._health_websocket:
                self._health_websocket.close()
        except Exception as e:
            Settings.logger.error(f"Error closing health WebSocket: {e}")
        finally:
            self._health_websocket = None

        # Reset connection state
        self._is_connected = False

        # Clear all event listeners
        self._safe_cleanup()

    def _check_connection(self, health_message: str):
        """Check if Pieces OS is connected and healthy."""
        health = health_message.lower() == "ok"

        if health and not self._is_connected:
            self._is_connected = True
            # Reset reconnect attempts on successful connection
            self._reconnect_attempts = 0
            self.emit(EventType.CONNECTION_ESTABLISHED, None)

        elif not health and self._is_connected:
            # Connection lost
            self._is_connected = False
            self.emit(EventType.CONNECTION_LOST, None)

    def is_connected(self) -> bool:
        """Check if currently connected."""
        return self._is_connected

    def reconnect(self):
        """Attempt to reconnect to Pieces OS with exponential backoff."""
        current_time = time.time()

        # Check if we've exceeded maximum reconnect attempts
        if self._reconnect_attempts >= self._max_reconnect_attempts:
            Settings.logger.error(
                f"Maximum reconnect attempts ({self._max_reconnect_attempts}) exceeded. "
                "Stopping reconnection attempts."
            )
            return

        # Implement exponential backoff
        if self._last_reconnect_time > 0:
            time_since_last_attempt = current_time - self._last_reconnect_time
            required_delay = self._base_reconnect_delay

            if time_since_last_attempt < required_delay:
                Settings.logger.info(
                    f"Reconnect too soon. Waiting {required_delay - time_since_last_attempt:.1f}s more"
                )
                return

        self._last_reconnect_time = current_time
        self._reconnect_attempts += 1

        Settings.logger.info(
            f"Reconnection attempt {self._reconnect_attempts}/{self._max_reconnect_attempts}"
        )

        try:
            if self._health_websocket:
                self._health_websocket.reconnect()
            else:
                # Create new WebSocket instance without recursion
                self._health_websocket = HealthWS.get_instance() or HealthWS(
                    pieces_client=Settings.pieces_client,
                    on_message_callback=self._check_connection,
                )
                # Start the WebSocket connection
                if hasattr(self._health_websocket, "start"):
                    self._health_websocket.start()

            self.emit(EventType.CONNECTION_RECONNECTING, None)

        except Exception as e:
            Settings.logger.error(f"Reconnection attempt failed: {e}")
            # Don't call reconnect() again - let the caller handle retry logic

    def reset_reconnect_state(self):
        """Reset reconnection state - useful when connection is manually restored."""
        self._reconnect_attempts = 0
        self._last_reconnect_time = 0
        Settings.logger.info("Reconnection state reset")
