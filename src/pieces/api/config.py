import pieces_os_client as pos_client
import importlib.resources
from pathlib import Path
import platform
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # same as used in django!


pieces_data_dir = importlib.resources.files(
    "pieces.data"
)  # our static packaged data files directory

applications_db_path = Path(
    pieces_data_dir,"applications.db"
)  # path to our applications.db

models_file  = Path(pieces_data_dir, "model_data.pkl") # model data file

platform_info = platform.platform()
if 'Linux' in platform_info:
    port = 5323
else:
    port = 1000
# Defining the host is optional and defaults to http://localhost:1000
# See configuration.py for a list of all supported configuration parameters.
configuration = pos_client.Configuration(host=f"http://localhost:{port}")


run_in_loop = False # is CLI looping?


# Initialize the ApiClient globally
api_client = pos_client.ApiClient(configuration)




