# SeededConnectorAsset

A generic model to use with the Connector API that requires little to no additional information about the current application.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**metadata** | [**SeededAssetMetadata**](SeededAssetMetadata.md) |  | [optional] 
**format** | [**SeededFormat**](SeededFormat.md) |  | 

## Example

```python
from openapi_client.models.seeded_connector_asset import SeededConnectorAsset

# TODO update the JSON string below
json = "{}"
# create an instance of SeededConnectorAsset from a JSON string
seeded_connector_asset_instance = SeededConnectorAsset.from_json(json)
# print the JSON string representation of the object
print SeededConnectorAsset.to_json()

# convert the object into a dict
seeded_connector_asset_dict = seeded_connector_asset_instance.to_dict()
# create an instance of SeededConnectorAsset from a dict
seeded_connector_asset_form_dict = seeded_connector_asset.from_dict(seeded_connector_asset_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


