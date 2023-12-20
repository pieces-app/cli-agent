# ReferencedActivity


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**reference** | [**FlattenedActivity**](FlattenedActivity.md) |  | [optional] 

## Example

```python
from openapi_client.models.referenced_activity import ReferencedActivity

# TODO update the JSON string below
json = "{}"
# create an instance of ReferencedActivity from a JSON string
referenced_activity_instance = ReferencedActivity.from_json(json)
# print the JSON string representation of the object
print ReferencedActivity.to_json()

# convert the object into a dict
referenced_activity_dict = referenced_activity_instance.to_dict()
# create an instance of ReferencedActivity from a dict
referenced_activity_form_dict = referenced_activity.from_dict(referenced_activity_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


