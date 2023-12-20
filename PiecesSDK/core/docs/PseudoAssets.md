# PseudoAssets

This is a model of all optional properties, that will get returned from /assets/pseudo.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**identifiers** | [**FlattenedAssets**](FlattenedAssets.md) |  | [optional] 

## Example

```python
from openapi_client.models.pseudo_assets import PseudoAssets

# TODO update the JSON string below
json = "{}"
# create an instance of PseudoAssets from a JSON string
pseudo_assets_instance = PseudoAssets.from_json(json)
# print the JSON string representation of the object
print PseudoAssets.to_json()

# convert the object into a dict
pseudo_assets_dict = pseudo_assets_instance.to_dict()
# create an instance of PseudoAssets from a dict
pseudo_assets_form_dict = pseudo_assets.from_dict(pseudo_assets_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


