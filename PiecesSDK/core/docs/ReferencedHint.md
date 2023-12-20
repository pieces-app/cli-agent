# ReferencedHint

This is the referenced version of a hint, main used for the uuid.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**reference** | [**FlattenedHint**](FlattenedHint.md) |  | [optional] 

## Example

```python
from openapi_client.models.referenced_hint import ReferencedHint

# TODO update the JSON string below
json = "{}"
# create an instance of ReferencedHint from a JSON string
referenced_hint_instance = ReferencedHint.from_json(json)
# print the JSON string representation of the object
print ReferencedHint.to_json()

# convert the object into a dict
referenced_hint_dict = referenced_hint_instance.to_dict()
# create an instance of ReferencedHint from a dict
referenced_hint_form_dict = referenced_hint.from_dict(referenced_hint_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


