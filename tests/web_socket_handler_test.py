# test_websocket_manager.py
import json
from unittest.mock import Mock, patch
import pytest
from src.pieces.api import WebSocketManager  # Replace with the actual module name

class TestWebSocketManager:

    @pytest.fixture
    def mock_websocket(self):
        with patch('websocket.WebSocketApp') as mock:
            yield mock

    @pytest.fixture
    def ws_manager(self):
        return WebSocketManager()

    def test_init(self, ws_manager):
        assert ws_manager.ws is None
        assert not ws_manager.is_connected
        assert ws_manager.response_received is None
        # ... assert other initial states

    def test_on_message(self, ws_manager):
        sample_message = json.dumps({
            'question': {
                'answers': {
                    'iterable': [{'text': 'Test answer'}]
                }
            },
            'status': 'COMPLETED'
        })
        ws_manager.on_message(None, sample_message)
        assert ws_manager.loading == False
        assert ws_manager.first_token_received

    def test_on_error(self, ws_manager):
        ws_manager.on_error(None, "Test error")
        assert not ws_manager.is_connected

    def test_on_close(self, ws_manager):
        ws_manager.on_close(None, None, None)
        assert not ws_manager.is_connected

    def test_on_open(self, ws_manager):
        ws_manager.on_open(None)
        assert ws_manager.is_connected

    def test_start_websocket_connection(self, ws_manager, mock_websocket):
        ws_manager.start_websocket_connection()
        mock_websocket.assert_called_once_with(
            "ws://localhost:1000/qgpt/stream",
            on_open=ws_manager.on_open,
            on_message=ws_manager.on_message,
            on_error=ws_manager.on_error,
            on_close=ws_manager.on_close
        )

    def test_send_message(self, ws_manager, mock_websocket):
        ws_manager.ws = Mock()
        ws_manager.is_connected = True
        ws_manager.query = "Test query"
        ws_manager.existing_model_id = "Test model"
        ws_manager.send_message()

        expected_message = {
            "question": {
                "query": "Test query",
                "relevant": {"iterable": []},
                "model": "Test model"
            }
        }
        ws_manager.ws.send.assert_called_with(json.dumps(expected_message))
