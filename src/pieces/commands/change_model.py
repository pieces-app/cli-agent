from pieces.gui import *
from pieces.settings import Settings

@deprecated("change_model","list models")
def change_model(**kwargs): # Change the model used in the ask command
    model_index = kwargs.get('MODEL_INDEX')
    try:
        if model_index:
            model_name = list(Settings.models.keys())[model_index-1] # because we begin from 1
            model_id  = Settings.models[model_name].get("uuid")
            Settings.model_id = model_id
            Settings.model_name = model_name
            Settings.dump_pickle(file = Settings.models_file,model_id = model_id)
            print(f"Switched to {model_name} with uuid {model_id}")
        else:
            raise Exception("Invalid model index or model index not provided.")
    except:
        print("Invalid model index or model index not provided.")
        print("Please choose from the list or use 'pieces list models'")
        


