import pieces_os_client as pos_client
import importlib.resources
from pathlib import Path

pieces_data_dir = importlib.resources.files(
    "pieces.data"
)  # our static packaged data files directory
applications_db_path = Path(
    "applications.db"
)  # path to our applications.db

# Defining the host is optional and defaults to http://localhost:1000
# See configuration.py for a list of all supported configuration parameters.
configuration = pos_client.Configuration(host="http://localhost:1000")

# Initialize the ApiClient globally
api_client = pos_client.ApiClient(configuration)

__all__ = ["api_client", 
            "applications_db_path",
            "pieces_data_dir",
            "pos_client"]