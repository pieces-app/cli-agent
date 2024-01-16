# FlattenedAnchorPoint


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**verified** | **bool** |  | [optional] 
**fullpath** | **str** | This is the text of the path. | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**platform** | [**PlatformEnum**](PlatformEnum.md) |  | [optional] 
**anchor** | [**ReferencedAnchor**](ReferencedAnchor.md) |  | 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_anchor_point import FlattenedAnchorPoint

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedAnchorPoint from a JSON string
flattened_anchor_point_instance = FlattenedAnchorPoint.from_json(json)
# print the JSON string representation of the object
print FlattenedAnchorPoint.to_json()

# convert the object into a dict
flattened_anchor_point_dict = flattened_anchor_point_instance.to_dict()
# create an instance of FlattenedAnchorPoint from a dict
flattened_anchor_point_form_dict = flattened_anchor_point.from_dict(flattened_anchor_point_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


