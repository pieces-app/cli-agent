# PKCE

An object representing all of the properties involved in a PKCE Authentication Flow

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**result** | [**ResultedPKCE**](ResultedPKCE.md) |  | [optional] 
**challenge** | [**ChallengedPKCE**](ChallengedPKCE.md) |  | [optional] 
**revocation** | [**RevokedPKCE**](RevokedPKCE.md) |  | [optional] 
**seed** | [**SeededPKCE**](SeededPKCE.md) |  | [optional] 
**token** | [**TokenizedPKCE**](TokenizedPKCE.md) |  | [optional] 
**auth0** | [**Auth0**](Auth0.md) |  | [optional] 

## Example

```python
from openapi_client.models.pkce import PKCE

# TODO update the JSON string below
json = "{}"
# create an instance of PKCE from a JSON string
pkce_instance = PKCE.from_json(json)
# print the JSON string representation of the object
print PKCE.to_json()

# convert the object into a dict
pkce_dict = pkce_instance.to_dict()
# create an instance of PKCE from a dict
pkce_form_dict = pkce.from_dict(pkce_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


