# SeededDiscoverableSensitive

This is the SeededDiscoverableSensitive, this has every property that the seededSensitive has except this one is all optionally passed in. and will override our classification if provided.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**asset** | **str** |  | 
**text** | **str** | this is the string representative of the sensative piece of data. | 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | [optional] 
**category** | [**SensitiveCategoryEnum**](SensitiveCategoryEnum.md) |  | [optional] 
**severity** | [**SensitiveSeverityEnum**](SensitiveSeverityEnum.md) |  | [optional] 
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**metadata** | [**SensitiveMetadata**](SensitiveMetadata.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_discoverable_sensitive import SeededDiscoverableSensitive

# TODO update the JSON string below
json = "{}"
# create an instance of SeededDiscoverableSensitive from a JSON string
seeded_discoverable_sensitive_instance = SeededDiscoverableSensitive.from_json(json)
# print the JSON string representation of the object
print SeededDiscoverableSensitive.to_json()

# convert the object into a dict
seeded_discoverable_sensitive_dict = seeded_discoverable_sensitive_instance.to_dict()
# create an instance of SeededDiscoverableSensitive from a dict
seeded_discoverable_sensitive_form_dict = seeded_discoverable_sensitive.from_dict(seeded_discoverable_sensitive_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


