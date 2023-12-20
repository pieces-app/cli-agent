# Sensitive

This is a fully referenced representation of a sensitive pieces of data.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**asset** | [**FlattenedAsset**](FlattenedAsset.md) |  | 
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
from openapi_client.models.sensitive import Sensitive

# TODO update the JSON string below
json = "{}"
# create an instance of Sensitive from a JSON string
sensitive_instance = Sensitive.from_json(json)
# print the JSON string representation of the object
print Sensitive.to_json()

# convert the object into a dict
sensitive_dict = sensitive_instance.to_dict()
# create an instance of Sensitive from a dict
sensitive_form_dict = sensitive.from_dict(sensitive_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


