# Format

A representation of Data for a particular Form Factor of an Asset.  Below asset HAS to be Flattened because it is a leaf node and must prevent cycles agressively.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**creator** | **str** |  | 
**classification** | [**Classification**](Classification.md) |  | 
**icon** | **str** |  | [optional] 
**role** | [**Role**](Role.md) |  | 
**application** | [**Application**](Application.md) |  | 
**asset** | [**FlattenedAsset**](FlattenedAsset.md) |  | 
**bytes** | [**ByteDescriptor**](ByteDescriptor.md) |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**synced** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**cloud** | **str** | This is a path used to determine what path this format lives at within the cloud. | [optional] 
**fragment** | [**FragmentFormat**](FragmentFormat.md) |  | [optional] 
**file** | [**FileFormat**](FileFormat.md) |  | [optional] 
**analysis** | [**Analysis**](Analysis.md) |  | [optional] 
**relationship** | [**Relationship**](Relationship.md) |  | [optional] 
**activities** | [**Activities**](Activities.md) |  | [optional] 

## Example

```python
from openapi_client.models.format import Format

# TODO update the JSON string below
json = "{}"
# create an instance of Format from a JSON string
format_instance = Format.from_json(json)
# print the JSON string representation of the object
print Format.to_json()

# convert the object into a dict
format_dict = format_instance.to_dict()
# create an instance of Format from a dict
format_form_dict = format.from_dict(format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


