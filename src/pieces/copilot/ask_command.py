from pieces.settings import Settings
from pieces.copilot.pieces_ask_websocket import AskWebsocket
import os
from pieces.gui import show_error
from pieces.assets.assets_api import AssetsCommandsApi

from pieces_os_client.models.referenced_asset import ReferencedAsset
from pieces_os_client.models.flattened_assets import FlattenedAssets
from pieces_os_client.models.qgpt_relevance_input import QGPTRelevanceInput
from pieces_os_client.api.qgpt_api import QGPTApi

ask_websocket = AskWebsocket()
def ask(query, **kwargs):
    relevant = {"iterable":[]}
    files = kwargs.get("files",None)
    snippets = kwargs.get("snippets",None)
    assets = []

    # Files
    if files:
        for idx,file in enumerate(files):
            if file == "/" or ".":
                files[idx] = os.getcwd()
                continue
            if os.path.exists(file): # check if file exists
                show_error(f"{file} is not found","Please enter a valid file path")
                return
            
            files[idx] = os.path.abspath(file) # Return the abs path
    # snippets
    if snippets:
        asset_ids = list(AssetsCommandsApi().assets_snapshot.keys())
        for idx,snippet in enumerate(snippets):
            try: asset_id = asset_ids[snippet-1] # we began enumerating from 1
            except KeyError: return show_error("Asset not found","Enter a vaild asset index")
            assets.append(ReferencedAsset(id=asset_id))
    

    # check for the assets
    flattened_assets = FlattenedAssets(iterable=assets) if assets else None

    if files or snippets:
        relevant = QGPTApi(Settings.api_client).relevance(
            QGPTRelevanceInput(
                            query=query,
                            paths=files,
                            assets=flattened_assets,
                            application=Settings.application.id,
                            model=Settings.model_id
                        )).to_dict()['relevant']
        
    ask_websocket.ask_question(Settings.model_id, query,relevant=relevant)

    