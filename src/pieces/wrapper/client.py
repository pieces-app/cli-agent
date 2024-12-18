from typing import TYPE_CHECKING, Optional,Dict, Union
import platform
import atexit
import subprocess
import urllib.request
import urllib.error

from .websockets.base_websocket import BaseWebsocket
from .api_client import PiecesApiClient

from .. import __version__

from .copilot import Copilot
from .basic_identifier.user import BasicUser
from .basic_identifier.asset import BasicAsset
from .streamed_identifiers import AssetSnapshot,ConversationsSnapshot
import time

if TYPE_CHECKING:
    from pieces_os_client.models.application import Application
    from pieces_os_client.models.fragment_metadata import FragmentMetadata
    from pieces_os_client.models.model import Model


class PiecesClient(PiecesApiClient):
    def __init__(self, host:str="", **kwargs):
        self._port = ""
        self.is_pos_stream_running = False
        self._reconnect_on_host_change = kwargs.get("reconnect_on_host_change", True)
        AssetSnapshot.pieces_client = self
        ConversationsSnapshot.pieces_client = self
        self._application = None
        self._copilot = None
        self.models:Dict[str, str] = {} # Maps model_name to the model_id
        self.models_object: list["Model"] = []
        self._is_started_runned = False
        self.local_os = platform.system().upper() if platform.system().upper() in ["WINDOWS","LINUX","DARWIN"] else "WEB"
        self.local_os = "MACOS" if self.local_os == "DARWIN" else self.local_os
        self._connect_websockets = kwargs.get("connect_websockets",True)
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
        from pieces_os_client.models.seeded_connector_connection import SeededConnectorConnection
        from pieces_os_client.models.seeded_tracked_application import SeededTrackedApplication
        
        if not self._application:
            self._application = self.connector_api.connect(seeded_connector_connection=SeededConnectorConnection(
                application=SeededTrackedApplication(
                    name = self.app_name,
                    platform = self.local_os,
                    version = __version__))).application
            self.api_client.set_default_header("application",self._application.id)
        
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
            self.user_websocket = AuthWS(self,self.user.on_user_callback)
            self.health_ws = HealthWS(self,lambda x : None)
            # Start all initilized websockets
            BaseWebsocket.start_all()
            
        return True
    
    @property
    def port(self) -> Union[str,None]:
        if not self._port: # check also if the HealthStream is running
            self.port = self._port_scanning()
        return self._port
        

    @port.setter
    def port(self, p: Union[str,None]):
        if p != self._port and p is not None:
            self.init_host("http://127.0.0.1:" + p,self._reconnect_on_host_change)
        self._port = p

    @property
    def host(self) -> str:
        if not self.port:
            return "http://127.0.0.1:39300"
        return "http://127.0.0.1:" + self.port

    @staticmethod
    def _port_scanning() -> Union[str,None]:
        for port in range(39300, 39334):
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/.well-known/health", timeout=1):
                    return str(port)
            except urllib.error.URLError:
                pass

        raise ValueError("PiecesOS is not running")

    def assets(self):
        """
            Retruns all the assets after the caching process is done
        """
        return [BasicAsset(id) for id in BasicAsset.identifiers_snapshot().keys()]

    def asset(self,asset_id):
        return BasicAsset(asset_id)

    @staticmethod
    def create_asset(content:str, metadata:Optional["FragmentMetadata"]=None):
        """
            Create an asset
        """
        return BasicAsset.create(content,metadata)


    def get_models(self) -> Dict[str, str]:
        """
            Returns a dict of the {model_name: model_id}
        """
        if not self.models:
            self.models_object = self.models_api.models_snapshot().iterable
            self.models = {model.name: model.id for model in self.models_object if model.cloud or model.downloaded} # getting the models that are available in the cloud or is downloaded
        return self.models

    @property
    def model_name(self):
        if hasattr(self,"_model_name"):
            return self._model_name
        return "GPT-3.5-turbo Chat Model"

    @property
    def model_id(self):
        if hasattr(self,"_model_id"):
            return self._model_id
        return self.get_models()[self.model_name]

    @model_name.setter
    def model_name(self,model):
        models = self.get_models()
        if model not in models:
            raise ValueError(f"Not a vaild model name, the available models are {', '.join(models.keys())}")
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
            Returns Pieces OS Version
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
            Open Pieces OS

            Returns (bool): true if Pieces OS runned successfully else false 
        """
        if self.is_pieces_running(): return True
        if self.local_os == "WINDOWS":
            subprocess.run(["start", "pieces://launch"], shell=True)
        elif self.local_os == "MACOS":
            subprocess.run(["open","pieces://launch"])
        elif self.local_os == "LINUX":
            subprocess.run(["xdg-open","pieces://launch"])
        return self.is_pieces_running(maxium_retries=6)


    def is_pieces_running(self,maxium_retries=1) -> bool:
        """
            Checks if Pieces OS is running or not

            Returns (bool): true if Pieces OS is running 
        """
        for _ in range(maxium_retries):
            try:
                with urllib.request.urlopen(f"{self.host}/.well-known/health", timeout=1) as response:
                    return response.status == 200
            except:
                time.sleep(1)
        return False


    def __str__(self) -> str:
        return f"<PiecesClient host={self.host}, pieces_os_status={'Running' if self.is_pieces_running() else 'Not running'}>"


    def __repr__(self) -> str:
        return f"<PiecesClient(host={self.host})>"


    def pool(self,api_call,args):
        """
            call the api async without stopping the main thread
            Create thread pool on first request
            avoids instantiating unused threadpool for blocking clients.
            return the ThreadPool created
        """
        return self.api_client.pool.apply_async(api_call, args)


# Register the function to be called on exit
atexit.register(PiecesClient.close)

