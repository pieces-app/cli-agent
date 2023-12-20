# SeededConversationMessage

This is a seeded version of a ConversationMessage.  conversation is optional, this is because it can be used within the SeededConversation, however if this is passed into the /messages/create w/o a conversation uuid then we will throw an error.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**model** | [**Model**](Model.md) |  | [optional] 
**fragment** | [**FragmentFormat**](FragmentFormat.md) |  | 
**conversation** | [**ReferencedConversation**](ReferencedConversation.md) |  | [optional] 
**sentiment** | [**ConversationMessageSentimentEnum**](ConversationMessageSentimentEnum.md) |  | [optional] 
**role** | [**QGPTConversationMessageRoleEnum**](QGPTConversationMessageRoleEnum.md) |  | 

## Example

```python
from openapi_client.models.seeded_conversation_message import SeededConversationMessage

# TODO update the JSON string below
json = "{}"
# create an instance of SeededConversationMessage from a JSON string
seeded_conversation_message_instance = SeededConversationMessage.from_json(json)
# print the JSON string representation of the object
print SeededConversationMessage.to_json()

# convert the object into a dict
seeded_conversation_message_dict = seeded_conversation_message_instance.to_dict()
# create an instance of SeededConversationMessage from a dict
seeded_conversation_message_form_dict = seeded_conversation_message.from_dict(seeded_conversation_message_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


