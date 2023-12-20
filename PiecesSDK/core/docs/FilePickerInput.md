# FilePickerInput

This is the input model for the FilePicker

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**allowed_extensions** | **List[str]** |  | [optional] 

## Example

```python
from openapi_client.models.file_picker_input import FilePickerInput

# TODO update the JSON string below
json = "{}"
# create an instance of FilePickerInput from a JSON string
file_picker_input_instance = FilePickerInput.from_json(json)
# print the JSON string representation of the object
print FilePickerInput.to_json()

# convert the object into a dict
file_picker_input_dict = file_picker_input_instance.to_dict()
# create an instance of FilePickerInput from a dict
file_picker_input_form_dict = file_picker_input.from_dict(file_picker_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


