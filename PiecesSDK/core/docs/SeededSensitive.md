# SeededSensitive

This is the seededSensitive, this does not have an id yet as we will add it on the server side.  can optionally pass in our mechanism here, as the default will be manual unless specified.  TODO consider updating these asset,format to referenced Models

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**asset** | **str** |  | 
**text** | **str** | this is the string representative of the sensative piece of data. | 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | [optional] 
**category** | [**SensitiveCategoryEnum**](SensitiveCategoryEnum.md) |  | 
**severity** | [**SensitiveSeverityEnum**](SensitiveSeverityEnum.md) |  | 
**name** | **str** |  | 
**description** | **str** |  | 
**metadata** | [**SensitiveMetadata**](SensitiveMetadata.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_sensitive import SeededSensitive

# TODO update the JSON string below
json = "{}"
# create an instance of SeededSensitive from a JSON string
seeded_sensitive_instance = SeededSensitive.from_json(json)
# print the JSON string representation of the object
print SeededSensitive.to_json()

# convert the object into a dict
seeded_sensitive_dict = seeded_sensitive_instance.to_dict()
# create an instance of SeededSensitive from a dict
seeded_sensitive_form_dict = seeded_sensitive.from_dict(seeded_sensitive_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


