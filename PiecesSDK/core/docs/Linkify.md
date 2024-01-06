# Linkify

This is the incoming linkify model.  if access is PRIVATE then please provide and array of users to enable the link for. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**seed** | [**Seed**](Seed.md) |  | [optional] 
**asset** | [**Asset**](Asset.md) |  | [optional] 
**users** | [**List[SeededUser]**](SeededUser.md) | this is an array of users. | [optional] 
**access** | [**AccessEnum**](AccessEnum.md) |  | 
**distributions** | [**SeededDistributions**](SeededDistributions.md) |  | [optional] 

## Example

```python
from openapi_client.models.linkify import Linkify

# TODO update the JSON string below
json = "{}"
# create an instance of Linkify from a JSON string
linkify_instance = Linkify.from_json(json)
# print the JSON string representation of the object
print Linkify.to_json()

# convert the object into a dict
linkify_dict = linkify_instance.to_dict()
# create an instance of Linkify from a dict
linkify_form_dict = linkify.from_dict(linkify_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


