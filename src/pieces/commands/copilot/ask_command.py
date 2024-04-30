from pieces.commands import commands_functions
from pieces.api.pieces_ask_websocket import WebSocketManager
from pieces_os_client import *
from pieces.settings import Settings
import os
from pieces.gui import show_error
from pieces.api.assets import get_assets_info_list

ws_manager = WebSocketManager()
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
        asset_ids = get_assets_info_list()
        for idx,snippet in enumerate(snippets):
            try: asset_id = asset_ids[snippet-1].get('id')  # we began enumerating from 1
            except: return show_error("Asset not found","Enter a vaild asset index")
            assets.append(ReferencedAsset(id=asset_id))
    

    # check for the assets
    flattened_assets = FlattenedAssets(iterable=assets) if assets else None

    if files or snippets:
        relevant = QGPTApi(Settings.api_client).relevance(
            QGPTRelevanceInput(
                            query=query,
                            paths=files,
                            assets=flattened_assets,
                            application=commands_functions.application.id,
                            model=commands_functions.model_id
                        )).to_dict()['relevant']
        
    ws_manager.ask_question(commands_functions.model_id, query,relevant=relevant)

    