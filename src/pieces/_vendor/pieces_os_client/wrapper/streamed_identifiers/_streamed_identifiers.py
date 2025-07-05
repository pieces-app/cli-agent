"""
A class for caching Streamed Identifiers. This class is designed to be inherited.

Attributes:
    identifiers_snapshot (Dict[str, Union[Asset, Conversation]]): A dictionary mapping IDs to their corresponding API call results.
    identifiers_queue (queue.Queue): A queue for IDs to be processed.
    identifiers_set (set): A set for IDs currently in the queue.
    _api_call (Callable[[str], Union[Asset, Conversation]]): A callable that takes an ID and returns either an Asset or a Conversation.
    block (bool): A flag to indicate whether to wait for the queue to receive the first ID.
    first_shot (bool): A flag to indicate if it's the first time to open the websocket.
    lock (threading.Lock): A lock for thread safety.
    worker_thread (threading.Thread): A thread for processing the queue.

Methods:
    worker(): Continuously processes IDs from the queue and updates the identifiers_snapshot.
    update_identifier(id: str): Updates the identifier snapshot with the result of the API call.
    streamed_identifiers_callback(ids: StreamedIdentifiers): Callback method to handle streamed identifiers.

Example:
    class AssetSnapshot(StreamedIdentifiersCache,_api_call=AssetApi(PiecesSettings.api_client).asset_snapshot):
        pass
"""

import queue
from typing import List, Union, Callable, TYPE_CHECKING
from abc import ABC, abstractmethod
import threading


if TYPE_CHECKING:
    from ..client import PiecesClient
    from pieces._vendor.pieces_os_client.models.streamed_identifiers import StreamedIdentifiers


class StreamedIdentifiersCache(ABC):
    """
    This class is made for caching Streamed Identifiers.
    Please use this class only as a parent class.
    """

    pieces_client: "PiecesClient"
    _initialized: threading.Event

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.on_update_list: List[Callable] = []
        cls.on_remove_list: List[Callable] = []
        cls.identifiers_snapshot = {}  # Map id:return from the _api_call
        cls.identifiers_queue = queue.Queue()  # Queue for ids to be processed
        cls.identifiers_set = set()  # Set for ids in the queue
        cls.block = True  # to wait for the queue to receive the first id
        cls.first_shot = True  # First time to open the websocket or not
        cls._lock = threading.Lock()  # Lock for thread safety
        cls._worker_thread = threading.Thread(target=cls.worker)
        cls._worker_thread.daemon = (
            True  # Ensure the thread exits when the main program does
        )

    @classmethod
    def on_update(cls, obj):
        for update in cls.on_update_list:
            update(obj)

    @classmethod
    def on_remove(cls, obj):
        for remove in cls.on_remove_list:
            remove(obj)

    @abstractmethod
    def _api_call(cls, id: str):
        pass

    @abstractmethod
    def _sort_first_shot(cls):
        """
        Sorting algorithm in the first shot
        """
        pass

    @abstractmethod
    def _name() -> str:
        pass

    @classmethod
    def worker(cls):
        while True:
            try:
                id = cls.identifiers_queue.get(block=cls.block, timeout=5)
                with cls._lock:
                    cls.identifiers_set.remove(id)  # Remove the id from the set
                cls.update_identifier(id)
                cls.identifiers_queue.task_done()
            except queue.Empty:  # queue is empty and the block is false
                if cls.block:
                    continue  # if there are more ids to load

                if cls.first_shot:
                    cls.first_shot = False
                    cls._initialized.set()
                    cls._sort_first_shot()

                return  # End the worker
            except Exception as e:
                print(f"Error in worker: {e}")

    @classmethod
    def update_identifier(cls, identifier: str):
        try:
            id_value = cls._api_call(identifier)
            with cls._lock:
                cls.identifiers_snapshot[identifier] = id_value
                cls.on_update(id_value)
            return id_value
        except Exception as e:
            print(f"Error updating identifier {identifier}: {e}")
            return None

    @classmethod
    def streamed_identifiers_callback(cls, ids: "StreamedIdentifiers"):
        # Start the worker thread if it's not running
        cls.block = True
        if not cls._worker_thread.is_alive():
            cls._worker_thread = threading.Thread(target=cls.worker)
            cls._worker_thread.daemon = True
            cls._worker_thread.start()

        for item in ids.iterable:
            reference_id = getattr(item, cls._name()).id

            with cls._lock:
                if reference_id not in cls.identifiers_set:
                    if item.deleted:
                        # Asset deleted
                        cls.on_remove(cls.identifiers_snapshot.pop(reference_id, None))
                    else:
                        if (
                            reference_id not in cls.identifiers_snapshot
                            and not cls.first_shot
                        ):
                            cls.identifiers_snapshot = {
                                reference_id: None,
                                **cls.identifiers_snapshot,
                            }
                        cls.identifiers_queue.put(reference_id)  # Add id to the queue
                        cls.identifiers_set.add(reference_id)  # Add id to the set

        cls.block = False  # Remove the block to end the thread
