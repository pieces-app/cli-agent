# ReferencedConversation

This is a DAG-Safe Minimal version of a Conversation.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**reference** | [**FlattenedConversation**](FlattenedConversation.md) |  | [optional] 

## Example

```python
from openapi_client.models.referenced_conversation import ReferencedConversation

# TODO update the JSON string below
json = "{}"
# create an instance of ReferencedConversation from a JSON string
referenced_conversation_instance = ReferencedConversation.from_json(json)
# print the JSON string representation of the object
print ReferencedConversation.to_json()

# convert the object into a dict
referenced_conversation_dict = referenced_conversation_instance.to_dict()
# create an instance of ReferencedConversation from a dict
referenced_conversation_form_dict = referenced_conversation.from_dict(referenced_conversation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


