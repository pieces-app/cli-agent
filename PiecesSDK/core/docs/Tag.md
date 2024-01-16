# Tag

This represents a fully polinated Tag, that is either attached to an asset or a format that adds additional information \"tags\" to describe itself.Helps improve Search and other contextual information that is useful for the user.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** | UUID that represents the tag. | 
**text** | **str** | represnts the value of a tag. | 
**mechanisms** | [**Dict[str, MechanismEnum]**](MechanismEnum.md) | This is a Map&lt;String, MechanismEnum&gt; where the the key is an asset id. | [optional] 
**assets** | [**FlattenedAssets**](FlattenedAssets.md) |  | [optional] 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**category** | [**TagCategoryEnum**](TagCategoryEnum.md) |  | 
**relationship** | [**Relationship**](Relationship.md) |  | [optional] 
**interactions** | **int** | This is an optional value that will keep track of the number of times this has been interacted with. | [optional] 
**persons** | [**FlattenedPersons**](FlattenedPersons.md) |  | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.tag import Tag

# TODO update the JSON string below
json = "{}"
# create an instance of Tag from a JSON string
tag_instance = Tag.from_json(json)
# print the JSON string representation of the object
print Tag.to_json()

# convert the object into a dict
tag_dict = tag_instance.to_dict()
# create an instance of Tag from a dict
tag_form_dict = tag.from_dict(tag_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


