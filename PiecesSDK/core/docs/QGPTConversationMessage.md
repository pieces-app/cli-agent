# QGPTConversationMessage

This will take a single message, and a role.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**text** | **str** |  | 
**role** | [**QGPTConversationMessageRoleEnum**](QGPTConversationMessageRoleEnum.md) |  | 
**timestamp** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 

## Example

```python
from openapi_client.models.qgpt_conversation_message import QGPTConversationMessage

# TODO update the JSON string below
json = "{}"
# create an instance of QGPTConversationMessage from a JSON string
qgpt_conversation_message_instance = QGPTConversationMessage.from_json(json)
# print the JSON string representation of the object
print QGPTConversationMessage.to_json()

# convert the object into a dict
qgpt_conversation_message_dict = qgpt_conversation_message_instance.to_dict()
# create an instance of QGPTConversationMessage from a dict
qgpt_conversation_message_form_dict = qgpt_conversation_message.from_dict(qgpt_conversation_message_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


