# Recipients

This an iterable of People that are attached to a specific distribution ie, slack, maigun, ...etc

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**iterable** | [**List[PersonBasicType]**](PersonBasicType.md) |  | 
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 

## Example

```python
from openapi_client.models.recipients import Recipients

# TODO update the JSON string below
json = "{}"
# create an instance of Recipients from a JSON string
recipients_instance = Recipients.from_json(json)
# print the JSON string representation of the object
print Recipients.to_json()

# convert the object into a dict
recipients_dict = recipients_instance.to_dict()
# create an instance of Recipients from a dict
recipients_form_dict = recipients.from_dict(recipients_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


