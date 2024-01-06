# SeededDiscoverableAsset

Assumption: filters applied in this model will overwrite filters passed in SeededDiscoverableAssets

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**file** | [**SeededFile**](SeededFile.md) |  | [optional] 
**fragment** | [**SeededFragment**](SeededFragment.md) |  | [optional] 
**directory** | **str** |  | [optional] 
**filters** | [**TLPDirectedDiscoveryFilters**](TLPDirectedDiscoveryFilters.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_discoverable_asset import SeededDiscoverableAsset

# TODO update the JSON string below
json = "{}"
# create an instance of SeededDiscoverableAsset from a JSON string
seeded_discoverable_asset_instance = SeededDiscoverableAsset.from_json(json)
# print the JSON string representation of the object
print SeededDiscoverableAsset.to_json()

# convert the object into a dict
seeded_discoverable_asset_dict = seeded_discoverable_asset_instance.to_dict()
# create an instance of SeededDiscoverableAsset from a dict
seeded_discoverable_asset_form_dict = seeded_discoverable_asset.from_dict(seeded_discoverable_asset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


