# FileFormat

This describes a FileFormat. If you need meta data you can get all of that from your format wrapper.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**bytes** | [**TransferableBytes**](TransferableBytes.md) |  | [optional] 
**string** | [**TransferableString**](TransferableString.md) |  | [optional] 

## Example

```python
from openapi_client.models.file_format import FileFormat

# TODO update the JSON string below
json = "{}"
# create an instance of FileFormat from a JSON string
file_format_instance = FileFormat.from_json(json)
# print the JSON string representation of the object
print FileFormat.to_json()

# convert the object into a dict
file_format_dict = file_format_instance.to_dict()
# create an instance of FileFormat from a dict
file_format_form_dict = file_format.from_dict(file_format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


