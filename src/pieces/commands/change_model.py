from pieces.settings import Settings

def change_model(**kwargs): # Change the model used in the ask command
    model_index = kwargs.get('MODEL_INDEX')
    if model_index:
        models = Settings.pieces_client.get_models()
        model_name = list(models.keys())[model_index-1] # because we begin from 1
        model_id  = models[model_name]
        Settings.pieces_client.model_id = model_id
        Settings.pieces_client.model_name = model_name
        Settings.dump_pickle(file = Settings.models_file,model_id = model_id)
        print(f"Switched to {model_name}")
    else:
        raise Exception("Invalid model index or model index not provided.")
        


