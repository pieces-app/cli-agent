## WEBSOCKET FUNCTIONS 
import json
import websocket
import threading
import pieces_os_client
from .config import run_in_loop


WEBSOCKET_URL = "ws://localhost:1000/qgpt/stream"
TIMEOUT = 20  # seconds




class WebSocketManager:
    def __init__(self):
        self.ws = None
        self.is_connected = False
        self.model_id = ""
        self.query = ""
        self.loading = False
        self.final_answer = ""
        self.conversation = None
        self.verbose = True
        self.message_compeleted = threading.Event()
    def open_websocket(self):
        """Opens a websocket connection"""
        self.open_event = threading.Event()  # wait for opening event
        self.start_thread = threading.Thread(target=self._start_ws)
        self.start_thread.start()
        self.open_event.wait()
        
    def on_message(self,ws, message):
        """Handle incoming websocket messages."""
        try:
            response = pieces_os_client.QGPTStreamOutput.from_json(message)
            if response.question:
                answers = response.question.answers.iterable
                for answer in answers:
                    text = answer.text
                    self.final_answer += text + " "
                    if text and self.verbose:
                        print(text, end='')

            if response.status == 'COMPLETED':
                print("\n")
                self.conversation = response.conversation
                if not run_in_loop and self.is_connected:
                    self.close_websocket_connection()

                self.message_compeleted.clear()

        except Exception as e:
            print(f"Error processing message: {e}")

    def on_error(self, ws, error):
        """Handle websocket errors."""
        print(f"WebSocket error: {error}")
        self.is_connected = False

    def on_close(self, ws, close_status_code, close_msg):
        """Handle websocket closure."""
        if self.verbose:
            print("WebSocket closed")
        self.is_connected = False

    def on_open(self, ws):
        """Handle websocket opening."""
        if self.verbose:
            print("WebSocket connection opened.")
        self.is_connected = True
        self.open_event.set()

    def _start_ws(self):
        """Start a new websocket connection."""
        if self.verbose:
            print("Starting WebSocket connection...")
        ws =  websocket.WebSocketApp(WEBSOCKET_URL,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_error=self.on_error,
                                         on_close=self.on_close)
        self.ws = ws
        ws.run_forever()
        

    def send_message(self):
        """Send a message over the websocket."""
        message = {
            "question": {
                "query": self.query,
                "relevant": {"iterable": []},
                "model": self.model_id
            },
            "conversation": self.conversation
        }
        json_message = json.dumps(message)

        if self.is_connected:
            try:
                self.ws.send(json_message)
                if self.verbose:
                    print("Response: ")
            except websocket.WebSocketException as e:
                print(f"Error sending message: {e}")
        else:
            self.open_websocket()
            self.send_message()

    def close_websocket_connection(self):
        """Close the websocket connection."""
        if self.ws and self.is_connected:
            self.ws.close()
            self.is_connected = False

    def ask_question(self, model_id, query,verbose = True):
        """Ask a question using the websocket."""
        if self.loading:
            return
        self.final_answer = ""
        self.loading = True
        self.model_id = model_id
        self.query = query
        self.verbose = verbose

        self.send_message()
        finishes = self.message_compeleted.wait(TIMEOUT)
        if not finishes:
            if not run_in_loop and self.is_connected:
                self.close_websocket_connection()
                self.message_compeleted.clear()
            raise ConnectionError("Failed to get the reponse back")
        return self.final_answer