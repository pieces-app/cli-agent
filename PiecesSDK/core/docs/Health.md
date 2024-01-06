# Health

This is a health model used to determine the \"health\" of the os server and cloud server(Coming Soon). READONLY Model.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**os** | [**OSHealth**](OSHealth.md) |  | 

## Example

```python
from openapi_client.models.health import Health

# TODO update the JSON string below
json = "{}"
# create an instance of Health from a JSON string
health_instance = Health.from_json(json)
# print the JSON string representation of the object
print Health.to_json()

# convert the object into a dict
health_dict = health_instance.to_dict()
# create an instance of Health from a dict
health_form_dict = health.from_dict(health_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


