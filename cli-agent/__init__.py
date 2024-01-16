import openapi_client
from openapi_client.rest import ApiException
from openapi_client.models.seeded_format import SeededFormat
from openapi_client.models.seeded_fragment import SeededFragment
from openapi_client.models.application import Application
from openapi_client.models.searched_assets import SearchedAssets 
from openapi_client.models.models import Models
from store import create_connection, get_application, insert_application, create_table
from openapi_client.models.qgpt_stream_input import QGPTStreamInput
from openapi_client.models.qgpt_question_input import QGPTQuestionInput
from openapi_client.models.qgpt_stream_output import QGPTStreamOutput
from openapi_client.models.relevant_qgpt_seed import RelevantQGPTSeed
from openapi_client.models.relevant_qgpt_seeds import RelevantQGPTSeeds
from openapi_client.models.format import Format
from openapi_client.models.seed import Seed
from openapi_client.models.exported_asset import ExportedAsset
from openapi_client.models.grouped_timestamp import GroupedTimestamp
from openapi_client.models.file_format import FileFormat
from openapi_client.models.classification import Classification
from pprint import pprint
import platform
import json
import websocket
import threading
import time
from datetime import datetime