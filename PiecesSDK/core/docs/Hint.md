# Hint

This is a hint that is attached to an asset, used for suggested_queries, and hints given via the qgpt flow.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | [optional] 
**asset** | [**ReferencedAsset**](ReferencedAsset.md) |  | [optional] 
**type** | [**HintTypeEnum**](HintTypeEnum.md) |  | 
**text** | **str** | This is the text of the hint. | 
**model** | [**ReferencedModel**](ReferencedModel.md) |  | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.hint import Hint

# TODO update the JSON string below
json = "{}"
# create an instance of Hint from a JSON string
hint_instance = Hint.from_json(json)
# print the JSON string representation of the object
print Hint.to_json()

# convert the object into a dict
hint_dict = hint_instance.to_dict()
# create an instance of Hint from a dict
hint_form_dict = hint.from_dict(hint_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


