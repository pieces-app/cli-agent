# FlattenedWebsite

This is a specific model for related websites to an asset.[DAG SAFE]

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** | this is aspecific uuid that represents | 
**assets** | [**FlattenedAssets**](FlattenedAssets.md) |  | [optional] 
**name** | **str** | A customizable name. | 
**url** | **str** | The true url or the website. | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**mechanisms** | [**Dict[str, MechanismEnum]**](MechanismEnum.md) | This is a Map&lt;String, MechanismEnum&gt; where the the key is an asset id. | [optional] 
**interactions** | **int** | This is an optional value that will keep track of the number of times this has been interacted with. | [optional] 
**persons** | [**FlattenedPersons**](FlattenedPersons.md) |  | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_website import FlattenedWebsite

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedWebsite from a JSON string
flattened_website_instance = FlattenedWebsite.from_json(json)
# print the JSON string representation of the object
print FlattenedWebsite.to_json()

# convert the object into a dict
flattened_website_dict = flattened_website_instance.to_dict()
# create an instance of FlattenedWebsite from a dict
flattened_website_form_dict = flattened_website.from_dict(flattened_website_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


