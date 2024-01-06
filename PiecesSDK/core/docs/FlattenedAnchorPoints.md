# FlattenedAnchorPoints


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**iterable** | [**List[ReferencedAnchorPoint]**](ReferencedAnchorPoint.md) |  | 
**indices** | **Dict[str, int]** | This is a Map&lt;String, int&gt; where the the key is an AnchorPoint id. | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_anchor_points import FlattenedAnchorPoints

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedAnchorPoints from a JSON string
flattened_anchor_points_instance = FlattenedAnchorPoints.from_json(json)
# print the JSON string representation of the object
print FlattenedAnchorPoints.to_json()

# convert the object into a dict
flattened_anchor_points_dict = flattened_anchor_points_instance.to_dict()
# create an instance of FlattenedAnchorPoints from a dict
flattened_anchor_points_form_dict = flattened_anchor_points.from_dict(flattened_anchor_points_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


