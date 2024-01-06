# SeededActivity

This is the preseed to a full blown Activity.  This is the minimum information needed to create an Activity, used within our [POST] /activities/create  if mechenism is not passed in we will default to AUTOMATIC  NOT required to pass in an asset/user/format.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**event** | [**SeededConnectorTracking**](SeededConnectorTracking.md) |  | 
**application** | [**Application**](Application.md) |  | 
**asset** | [**ReferencedAsset**](ReferencedAsset.md) |  | [optional] 
**user** | [**ReferencedUser**](ReferencedUser.md) |  | [optional] 
**format** | [**ReferencedFormat**](ReferencedFormat.md) |  | [optional] 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_activity import SeededActivity

# TODO update the JSON string below
json = "{}"
# create an instance of SeededActivity from a JSON string
seeded_activity_instance = SeededActivity.from_json(json)
# print the JSON string representation of the object
print SeededActivity.to_json()

# convert the object into a dict
seeded_activity_dict = seeded_activity_instance.to_dict()
# create an instance of SeededActivity from a dict
seeded_activity_form_dict = seeded_activity.from_dict(seeded_activity_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


