# SeededDiscoverableAssets

Assumption: filters imposed in this model can be overwritten by passing them in SeededDiscoverableAsset

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**application** | **str** | application id. | 
**iterable** | [**List[SeededDiscoverableAsset]**](SeededDiscoverableAsset.md) | This is an iterable of already snippitized snippets that we will compare &amp;&amp; cluster. | 
**filters** | [**TLPDirectedDiscoveryFilters**](TLPDirectedDiscoveryFilters.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_discoverable_assets import SeededDiscoverableAssets

# TODO update the JSON string below
json = "{}"
# create an instance of SeededDiscoverableAssets from a JSON string
seeded_discoverable_assets_instance = SeededDiscoverableAssets.from_json(json)
# print the JSON string representation of the object
print SeededDiscoverableAssets.to_json()

# convert the object into a dict
seeded_discoverable_assets_dict = seeded_discoverable_assets_instance.to_dict()
# create an instance of SeededDiscoverableAssets from a dict
seeded_discoverable_assets_form_dict = seeded_discoverable_assets.from_dict(seeded_discoverable_assets_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


