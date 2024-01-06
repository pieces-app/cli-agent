# Tags

This is a model that represents multiple Tag Models

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**iterable** | [**List[Tag]**](Tag.md) |  | 
**indices** | **Dict[str, int]** | This is a Map&lt;String, int&gt; where the the key is an tag id. | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.tags import Tags

# TODO update the JSON string below
json = "{}"
# create an instance of Tags from a JSON string
tags_instance = Tags.from_json(json)
# print the JSON string representation of the object
print Tags.to_json()

# convert the object into a dict
tags_dict = tags_instance.to_dict()
# create an instance of Tags from a dict
tags_form_dict = tags.from_dict(tags_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


