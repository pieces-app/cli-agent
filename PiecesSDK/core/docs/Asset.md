# Asset

An Asset Model representing data extracted from an Application connecting a group of data containing one or more Formats.  Below formats, preview, and original CAN to be pollinated (DAG Unsafe) because it is a root node and it's child leaf nodes will prevent cycles agressively.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** | The globally available UID representing the asset in the Database, both locally and in the cloud. | 
**name** | **str** |  | [optional] 
**creator** | **str** |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**synced** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**formats** | [**Formats**](Formats.md) |  | 
**preview** | [**Preview**](Preview.md) |  | 
**original** | [**ReferencedFormat**](ReferencedFormat.md) |  | 
**shares** | [**Shares**](Shares.md) |  | [optional] 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | 
**websites** | [**Websites**](Websites.md) |  | [optional] 
**interacted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**tags** | [**Tags**](Tags.md) |  | [optional] 
**sensitives** | [**Sensitives**](Sensitives.md) |  | [optional] 
**persons** | [**Persons**](Persons.md) |  | [optional] 
**curated** | **bool** | This is an optional boolean that will flag that this asset came from a currated collection. | [optional] 
**discovered** | **bool** |  | [optional] 
**activities** | [**Activities**](Activities.md) |  | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 
**favorited** | **bool** |  | [optional] 
**pseudo** | **bool** | This will determine if this is a asset that the user did not explicitly save. | [optional] 
**annotations** | [**Annotations**](Annotations.md) |  | [optional] 
**hints** | [**Hints**](Hints.md) |  | [optional] 
**anchors** | [**Anchors**](Anchors.md) |  | [optional] 
**conversations** | [**Conversations**](Conversations.md) |  | [optional] 

## Example

```python
from openapi_client.models.asset import Asset

# TODO update the JSON string below
json = "{}"
# create an instance of Asset from a JSON string
asset_instance = Asset.from_json(json)
# print the JSON string representation of the object
print Asset.to_json()

# convert the object into a dict
asset_dict = asset_instance.to_dict()
# create an instance of Asset from a dict
asset_form_dict = asset.from_dict(asset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


