# FlattenedPerson

if expiration is add then, after the alloted expiration date the user will only have view && comment only permissions. Only present in the case there is a scope such as a defined collection/asset...  if asset is passed then that means this person belongs to a scoped asset.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**type** | [**PersonType**](PersonType.md) |  | 
**assets** | [**FlattenedAssets**](FlattenedAssets.md) |  | [optional] 
**mechanisms** | [**Dict[str, MechanismEnum]**](MechanismEnum.md) | This is a Map&lt;String, MechanismEnum&gt; where the the key is an asset id. | [optional] 
**interactions** | **int** | This is an optional value that will keep track of the number of times this has been interacted with. | [optional] 
**access** | [**Dict[str, PersonAccess]**](PersonAccess.md) | This is a Map&lt;String, PersonAccess&gt; where the the key is an asset id. | [optional] 
**tags** | [**FlattenedTags**](FlattenedTags.md) |  | [optional] 
**websites** | [**FlattenedWebsites**](FlattenedWebsites.md) |  | [optional] 
**models** | [**Dict[str, PersonModel]**](PersonModel.md) | This is a Map&lt;String, PersonModel&gt;, where the the key is an asset id. | [optional] 
**annotations** | [**FlattenedAnnotations**](FlattenedAnnotations.md) |  | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_person import FlattenedPerson

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedPerson from a JSON string
flattened_person_instance = FlattenedPerson.from_json(json)
# print the JSON string representation of the object
print FlattenedPerson.to_json()

# convert the object into a dict
flattened_person_dict = flattened_person_instance.to_dict()
# create an instance of FlattenedPerson from a dict
flattened_person_form_dict = flattened_person.from_dict(flattened_person_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


