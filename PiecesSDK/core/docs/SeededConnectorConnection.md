# SeededConnectorConnection

A model that is passed to the context API at bootup

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**application** | [**SeededTrackedApplication**](SeededTrackedApplication.md) |  | 

## Example

```python
from openapi_client.models.seeded_connector_connection import SeededConnectorConnection

# TODO update the JSON string below
json = "{}"
# create an instance of SeededConnectorConnection from a JSON string
seeded_connector_connection_instance = SeededConnectorConnection.from_json(json)
# print the JSON string representation of the object
print SeededConnectorConnection.to_json()

# convert the object into a dict
seeded_connector_connection_dict = seeded_connector_connection_instance.to_dict()
# create an instance of SeededConnectorConnection from a dict
seeded_connector_connection_form_dict = seeded_connector_connection.from_dict(seeded_connector_connection_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


