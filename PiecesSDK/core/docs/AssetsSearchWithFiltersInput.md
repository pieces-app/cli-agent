# AssetsSearchWithFiltersInput


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**query** | **str** |  | [optional] 
**space** | [**AssetSearchSpace**](AssetSearchSpace.md) |  | [optional] 
**filters** | [**AssetFilters**](AssetFilters.md) |  | [optional] 
**casing** | **bool** | This is an optional bool that will let us know, if we want to ignore case or not.(default is to allow casing)ie casing:true. | [optional] 

## Example

```python
from openapi_client.models.assets_search_with_filters_input import AssetsSearchWithFiltersInput

# TODO update the JSON string below
json = "{}"
# create an instance of AssetsSearchWithFiltersInput from a JSON string
assets_search_with_filters_input_instance = AssetsSearchWithFiltersInput.from_json(json)
# print the JSON string representation of the object
print AssetsSearchWithFiltersInput.to_json()

# convert the object into a dict
assets_search_with_filters_input_dict = assets_search_with_filters_input_instance.to_dict()
# create an instance of AssetsSearchWithFiltersInput from a dict
assets_search_with_filters_input_form_dict = assets_search_with_filters_input.from_dict(assets_search_with_filters_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


