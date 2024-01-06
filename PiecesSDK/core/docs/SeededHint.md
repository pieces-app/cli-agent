# SeededHint


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | [optional] 
**asset** | **str** | This is an asset id that we are using to link this to an asset. | [optional] 
**type** | [**HintTypeEnum**](HintTypeEnum.md) |  | 
**text** | **str** | This is the text of the hint. | 
**model** | **str** | this is a model id. that we are using to link this to a model. | [optional] 

## Example

```python
from openapi_client.models.seeded_hint import SeededHint

# TODO update the JSON string below
json = "{}"
# create an instance of SeededHint from a JSON string
seeded_hint_instance = SeededHint.from_json(json)
# print the JSON string representation of the object
print SeededHint.to_json()

# convert the object into a dict
seeded_hint_dict = seeded_hint_instance.to_dict()
# create an instance of SeededHint from a dict
seeded_hint_form_dict = seeded_hint.from_dict(seeded_hint_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


