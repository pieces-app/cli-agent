# Users

A base class for a collection of users and some additional meta properties.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**iterable** | [**List[UserProfile]**](UserProfile.md) |  | [optional] 

## Example

```python
from openapi_client.models.users import Users

# TODO update the JSON string below
json = "{}"
# create an instance of Users from a JSON string
users_instance = Users.from_json(json)
# print the JSON string representation of the object
print Users.to_json()

# convert the object into a dict
users_dict = users_instance.to_dict()
# create an instance of Users from a dict
users_form_dict = users.from_dict(users_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


