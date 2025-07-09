from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import TYPE_CHECKING, Optional, Dict, Union, Callable
import platform
import atexit
import urllib.request
import urllib.error
import webbrowser
import socket

from .websockets.base_websocket import BaseWebsocket
from .api_client import PiecesApiClient

from .. import __version__

from .copilot import Copilot
from .basic_identifier.user import BasicUser
from .basic_identifier.asset import BasicAsset
from .installation import PosInstaller, DownloadModel
from .streamed_identifiers._streamed_identifiers import StreamedIdentifiersCache
import time

if TYPE_CHECKING:
    from pieces._vendor.pieces_os_client.models.application import Application
    from pieces._vendor.pieces_os_client.models.fragment_metadata import FragmentMetadata
    from pieces._vendor.pieces_os_client.models.model import Model


class PiecesClient(PiecesApiClient):
    def __init__(self, host: str = "", **kwargs):
        self._port = ""
        self.is_pos_stream_running = False
        self._reconnect_on_host_change = kwargs.get(
            "reconnect_on_host_change", True)
        StreamedIdentifiersCache.pieces_client = self
        self._application = None
        self._copilot = None
        self.models: Dict[str, str] = {}  # Maps model_name to the model_id
        self.models_object: list["Model"] = []
        self._is_started_runned = False
        self.local_os = platform.system().upper() if platform.system().upper() in [
            "WINDOWS", "LINUX", "DARWIN"] else "WEB"
        self.local_os = "MACOS" if self.local_os == "DARWIN" else self.local_os
        self._connect_websockets = kwargs.get("connect_websockets", True)
        self.user = BasicUser(self)
        self.app_name = "PIECES_FOR_DEVELOPERS_CLI"
        super().__init__()

    @property
    def copilot(self):
        if not self._copilot:
            self._copilot = Copilot(self)
        return self._copilot

    @property
    def application(self) -> "Application":
        from pieces._vendor.pieces_os_client.models.seeded_connector_connection import SeededConnectorConnection
        from pieces._vendor.pieces_os_client.models.seeded_tracked_application import SeededTrackedApplication

        if not self._application:
            self._application = self.connector_api.connect(
                seeded_connector_connection=SeededConnectorConnection(
                    application=SeededTrackedApplication(
                        name=self.app_name,
                        platform=self.local_os,
                        version=__version__))).application
            self.api_client.set_default_header(
                "application", self._application.id)

        return self._application

    def connect_websocket(self) -> bool:
        from .websockets.conversations_ws import ConversationWS
        from .websockets.assets_identifiers_ws import AssetsIdentifiersWS
        from .websockets.health_ws import HealthWS
        from .websockets.auth_ws import AuthWS

        if self._is_started_runned:
            return True
        if not self.is_pieces_running():
            return False

        self._is_started_runned = True
        if self._connect_websockets:
            self.conversation_ws = ConversationWS(self)
            self.assets_ws = AssetsIdentifiersWS(self)
            self.user_websocket = AuthWS(self, self.user.on_user_callback)
            self.health_ws = HealthWS(self, lambda x: None)
            # Start all initilized websockets
            BaseWebsocket.start_all()

        return True

    @property
    def port(self) -> Union[str, None]:
        if not self._port:  # check also if the HealthStream is running
            self.port = self._port_scanning()
        return self._port

    @port.setter
    def port(self, p: Union[str, None]):
        if p != self._port and p is not None:
            self.init_host("http://127.0.0.1:" + p,
                           self._reconnect_on_host_change)
        self._port = p

    @property
    def host(self) -> str:
        if not self.port:
            return "http://127.0.0.1:39300"
        return "http://127.0.0.1:" + self.port

    @staticmethod
    def _port_scanning() -> str:
        def check_port(port: int) -> Optional[str]:
            try:
                # 1) Quick socket check
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(0.05)  # Short timeout for local checks
                    if sock.connect_ex(('127.0.0.1', port)) != 0:
                        return None  # If non-zero, the socket isn't open

                # 2) If socket is open, send a single HEAD request
                url = f"http://127.0.0.1:{port}/.well-known/health"
                request = urllib.request.Request(url, method='HEAD')
                with urllib.request.urlopen(request, timeout=0.1) as response:
                    if response.status == 200:
                        return str(port)
            except Exception:
                pass
            return None

        # Scan ports 39300 to 39334 in parallel
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(check_port, p)
                       for p in range(39300, 39334)]
            for future in as_completed(futures):
                result = future.result()
                if result is not None:
                    return result

        # If no port was found, raise an error
        raise ValueError("PiecesOS is not running")

    def assets(self):
        """
            Retruns all the assets after the caching process is done
        """
        return [BasicAsset(id) for id in BasicAsset.identifiers_snapshot().keys()]

    def asset(self, asset_id):
        return BasicAsset(asset_id)

    @staticmethod
    def create_asset(content: str, metadata: Optional["FragmentMetadata"] = None):
        """
            Create an asset
        """
        return BasicAsset.create(content, metadata)

    def get_models(self) -> Dict[str, str]:
        """
            Returns a dict of the {model_name: model_id}
        """
        if not self.models:
            self.models_object = self.models_api.models_snapshot().iterable
            # getting the models that are available in the cloud or is downloaded
            self.models = {
                model.name: model.id for model in self.models_object if model.cloud or model.downloaded}
        return self.models

    @property
    def model_name(self):
        if hasattr(self, "_model_name"):
            return self._model_name
        return "GPT-3.5-turbo Chat Model"

    @property
    def model_id(self):
        if hasattr(self, "_model_id"):
            return self._model_id
        return self.get_models()[self.model_name]

    @model_name.setter
    def model_name(self, model):
        models = self.get_models()
        if model not in models:
            raise ValueError("Not a vaild model name, the available models are"
                             f"{', '.join(models.keys())}")
        self._model_name = model
        self._model_id = models[model]

    @property
    def available_models_names(self) -> list:
        """
            Returns all available models names
        """
        return list(self.get_models().keys())

    @classmethod
    def close(cls):
        """
            Use this when you exit the app
        """
        BaseWebsocket.close_all()
        if hasattr(atexit, 'unregister'):
            atexit.unregister(cls.close)

    @property
    def version(self) -> str:
        """
            Returns PiecesOS Version
        """
        return self.well_known_api.get_well_known_version()

    @property
    def health(self) -> str:
        """
            Calls the well known health api
            /.well-known/health [GET]
        """
        return self.well_known_api.get_well_known_health()

    def open_pieces_os(self) -> bool:
        """
            Open PiecesOS

            Returns (bool): true if PiecesOS launches successfully
        """
        uri = "pieces://launch"
        if self.is_pieces_running():
            return True
        try:
            sucess = webbrowser.open(uri)
            if not sucess:
                return False
        except:
            return False
        return self.is_pieces_running(maximum_retries=12)

    def is_pieces_running(self, maximum_retries=1) -> bool:
        """
            Checks if PiecesOS is running or not

            Returns (bool): true if PiecesOS is running 
        """
        for _ in range(maximum_retries):
            try:
                with urllib.request.urlopen(f"{self.host}/.well-known/health", timeout=1) as response:
                    return response.status == 200
            except:
                if maximum_retries == 1:
                    return False
                time.sleep(1)
        return False

    def __str__(self) -> str:
        return f"<PiecesClient host={self.host}, pieces_os_status={'Running' if self.is_pieces_running() else 'Not running'}>"

    def __repr__(self) -> str:
        return f"<PiecesClient(host={self.host})>"

    def pieces_os_installer(self, callback: Callable[[DownloadModel], None]) -> PosInstaller:
        """
        Installs Pieces OS using the provided callback for download progress updates.

        Args:
            callback (Callable[[DownloadModel], None]): A callback function to receive download progress updates.

        Returns:
            PosInstaller: An instance of PosInstaller handling the installation process.
        """
        return PosInstaller(callback, self.app_name)

    def pool(self, api_call, args):
        """
            call the api async without stopping the main thread
            Create thread pool on first request
            avoids instantiating unused threadpool for blocking clients.
            return the ThreadPool created
        """
        return self.api_client.pool.apply_async(api_call, args)


# Register the function to be called on exit
atexit.register(PiecesClient.close)
