# FlattenedAnchors


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**iterable** | [**List[ReferencedAnchor]**](ReferencedAnchor.md) |  | 
**indices** | **Dict[str, int]** | This is a Map&lt;String, int&gt; where the the key is an Anchor id. | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_anchors import FlattenedAnchors

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedAnchors from a JSON string
flattened_anchors_instance = FlattenedAnchors.from_json(json)
# print the JSON string representation of the object
print FlattenedAnchors.to_json()

# convert the object into a dict
flattened_anchors_dict = flattened_anchors_instance.to_dict()
# create an instance of FlattenedAnchors from a dict
flattened_anchors_form_dict = flattened_anchors.from_dict(flattened_anchors_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


