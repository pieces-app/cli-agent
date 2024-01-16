# AssetFilter

** in the future, consider adding an optional bool's called nextAnd, nextOr which will say that the next filter will be  AND behavor or OR behavior.  \"operations\": here is is an optional property to allow or behavior,(we will only allow 1 level deep of or's), if or is not passed in then it is just simply ignored. If or is passed in then we will be or'd together with the top level filter and considered extras. default behavior for operations is and, however yoour can specifiy OR operations as well.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**classification** | [**ClassificationSpecificEnum**](ClassificationSpecificEnum.md) |  | [optional] 
**tags** | **List[str]** |  | [optional] 
**websites** | **List[str]** |  | [optional] 
**persons** | **List[str]** |  | [optional] 
**phrase** | [**AssetFilterPhrase**](AssetFilterPhrase.md) |  | [optional] 
**created** | [**AssetFilterTimestamp**](AssetFilterTimestamp.md) |  | [optional] 
**updated** | [**AssetFilterTimestamp**](AssetFilterTimestamp.md) |  | [optional] 
**operations** | [**AssetFilters**](AssetFilters.md) |  | [optional] 

## Example

```python
from openapi_client.models.asset_filter import AssetFilter

# TODO update the JSON string below
json = "{}"
# create an instance of AssetFilter from a JSON string
asset_filter_instance = AssetFilter.from_json(json)
# print the JSON string representation of the object
print AssetFilter.to_json()

# convert the object into a dict
asset_filter_dict = asset_filter_instance.to_dict()
# create an instance of AssetFilter from a dict
asset_filter_form_dict = asset_filter.from_dict(asset_filter_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


