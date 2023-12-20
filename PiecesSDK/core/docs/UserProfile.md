# UserProfile

This is the model for a user logged into Pieces.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**picture** | **str** | mapped from picture.URL pointing to the user&#39;s profile picture.  | [optional] [default to 'https://picsum.photos/200']
**email** | **str** |  | [optional] [default to 'user@pieces.app']
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**username** | **str** |  (unique) User&#39;s username.   | [optional] 
**id** | **str** |  | 
**name** | **str** | This is the name of the User. | [optional] 
**aesthetics** | [**Aesthetics**](Aesthetics.md) |  | 
**vanityname** | **str** |  | [optional] 
**allocation** | [**AllocationCloud**](AllocationCloud.md) |  | [optional] 
**providers** | [**ExternalProviders**](ExternalProviders.md) |  | [optional] 
**auth0** | [**Auth0UserMetadata**](Auth0UserMetadata.md) |  | [optional] 

## Example

```python
from openapi_client.models.user_profile import UserProfile

# TODO update the JSON string below
json = "{}"
# create an instance of UserProfile from a JSON string
user_profile_instance = UserProfile.from_json(json)
# print the JSON string representation of the object
print UserProfile.to_json()

# convert the object into a dict
user_profile_dict = user_profile_instance.to_dict()
# create an instance of UserProfile from a dict
user_profile_form_dict = user_profile.from_dict(user_profile_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


