# FlattenedSensitive

This is a dereferenced representation of a sensitive pieces of data.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**asset** | [**ReferencedAsset**](ReferencedAsset.md) |  | 
**text** | **str** |  | 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | 
**category** | [**SensitiveCategoryEnum**](SensitiveCategoryEnum.md) |  | 
**severity** | [**SensitiveSeverityEnum**](SensitiveSeverityEnum.md) |  | 
**name** | **str** |  | 
**description** | **str** |  | 
**metadata** | [**SensitiveMetadata**](SensitiveMetadata.md) |  | [optional] 
**interactions** | **int** | This is an optional value that will keep track of the number of times this has been interacted with. | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_sensitive import FlattenedSensitive

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedSensitive from a JSON string
flattened_sensitive_instance = FlattenedSensitive.from_json(json)
# print the JSON string representation of the object
print FlattenedSensitive.to_json()

# convert the object into a dict
flattened_sensitive_dict = flattened_sensitive_instance.to_dict()
# create an instance of FlattenedSensitive from a dict
flattened_sensitive_form_dict = flattened_sensitive.from_dict(flattened_sensitive_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


