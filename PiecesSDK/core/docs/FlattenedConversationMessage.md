# FlattenedConversationMessage

This is a flattened DAG safe version of a ConversationMessage.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**model** | [**Model**](Model.md) |  | [optional] 
**fragment** | [**FragmentFormat**](FragmentFormat.md) |  | [optional] 
**conversation** | [**ReferencedConversation**](ReferencedConversation.md) |  | 
**sentiment** | [**ConversationMessageSentimentEnum**](ConversationMessageSentimentEnum.md) |  | [optional] 
**role** | [**QGPTConversationMessageRoleEnum**](QGPTConversationMessageRoleEnum.md) |  | 
**score** | [**Score**](Score.md) |  | [optional] 
**annotations** | [**FlattenedAnnotations**](FlattenedAnnotations.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_conversation_message import FlattenedConversationMessage

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedConversationMessage from a JSON string
flattened_conversation_message_instance = FlattenedConversationMessage.from_json(json)
# print the JSON string representation of the object
print FlattenedConversationMessage.to_json()

# convert the object into a dict
flattened_conversation_message_dict = flattened_conversation_message_instance.to_dict()
# create an instance of FlattenedConversationMessage from a dict
flattened_conversation_message_form_dict = flattened_conversation_message.from_dict(flattened_conversation_message_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


