# PersonAccess

if scoped is provided will let us know what level of permission(access) this specific person has in relation to what scope.(collection, asset,...etc)  in the future will expand to global (with its own enumeration for a global entire project/cloud scope)

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**scoped** | [**PersonAccessScopedEnum**](PersonAccessScopedEnum.md) |  | [optional] 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 

## Example

```python
from openapi_client.models.person_access import PersonAccess

# TODO update the JSON string below
json = "{}"
# create an instance of PersonAccess from a JSON string
person_access_instance = PersonAccess.from_json(json)
# print the JSON string representation of the object
print PersonAccess.to_json()

# convert the object into a dict
person_access_dict = person_access_instance.to_dict()
# create an instance of PersonAccess from a dict
person_access_form_dict = person_access.from_dict(person_access_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


