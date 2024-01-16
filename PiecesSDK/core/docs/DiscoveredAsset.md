# DiscoveredAsset



## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**file** | [**SeededFile**](SeededFile.md) |  | [optional] 
**fragment** | [**SeededFragment**](SeededFragment.md) |  | [optional] 
**directory** | **str** |  | [optional] 
**metadata** | [**SeededAssetMetadata**](SeededAssetMetadata.md) |  | [optional] 
**filters** | [**TLPDirectedDiscoveryFilters**](TLPDirectedDiscoveryFilters.md) |  | [optional] 

## Example

```python
from openapi_client.models.discovered_asset import DiscoveredAsset

# TODO update the JSON string below
json = "{}"
# create an instance of DiscoveredAsset from a JSON string
discovered_asset_instance = DiscoveredAsset.from_json(json)
# print the JSON string representation of the object
print DiscoveredAsset.to_json()

# convert the object into a dict
discovered_asset_dict = discovered_asset_instance.to_dict()
# create an instance of DiscoveredAsset from a dict
discovered_asset_form_dict = discovered_asset.from_dict(discovered_asset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


