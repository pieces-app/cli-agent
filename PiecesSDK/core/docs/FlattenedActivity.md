# FlattenedActivity

Note: - if mechanism == internal we will not display to the user.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**event** | [**SeededConnectorTracking**](SeededConnectorTracking.md) |  | 
**application** | [**Application**](Application.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**asset** | [**ReferencedAsset**](ReferencedAsset.md) |  | [optional] 
**format** | [**ReferencedFormat**](ReferencedFormat.md) |  | [optional] 
**user** | [**FlattenedUserProfile**](FlattenedUserProfile.md) |  | [optional] 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | 
**rank** | **int** |  | [optional] 

## Example

```python
from openapi_client.models.flattened_activity import FlattenedActivity

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedActivity from a JSON string
flattened_activity_instance = FlattenedActivity.from_json(json)
# print the JSON string representation of the object
print FlattenedActivity.to_json()

# convert the object into a dict
flattened_activity_dict = flattened_activity_instance.to_dict()
# create an instance of FlattenedActivity from a dict
flattened_activity_form_dict = flattened_activity.from_dict(flattened_activity_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


