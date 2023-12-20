# FlattenedActivities


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**iterable** | [**List[ReferencedActivity]**](ReferencedActivity.md) |  | 

## Example

```python
from openapi_client.models.flattened_activities import FlattenedActivities

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedActivities from a JSON string
flattened_activities_instance = FlattenedActivities.from_json(json)
# print the JSON string representation of the object
print FlattenedActivities.to_json()

# convert the object into a dict
flattened_activities_dict = flattened_activities_instance.to_dict()
# create an instance of FlattenedActivities from a dict
flattened_activities_form_dict = flattened_activities.from_dict(flattened_activities_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


