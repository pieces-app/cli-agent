# FlattenedConversation

This is a flattend version of the Convsersation for DAG-Safety.  This will hold together a conversation. Ie allthe message within a conversation.  All the additional properties on here used on here like(anchors/assets) are used for context that will seed the conversation.  model is a calculated property, and will be the model of the last message sent if applicable.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**name** | **str** | This is a name that is customized. | [optional] 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**favorited** | **bool** |  | [optional] 
**application** | [**Application**](Application.md) |  | [optional] 
**annotations** | [**FlattenedAnnotations**](FlattenedAnnotations.md) |  | [optional] 
**messages** | [**FlattenedConversationMessages**](FlattenedConversationMessages.md) |  | 
**model** | [**ReferencedModel**](ReferencedModel.md) |  | [optional] 
**assets** | [**FlattenedAssets**](FlattenedAssets.md) |  | [optional] 
**anchors** | [**FlattenedAnchors**](FlattenedAnchors.md) |  | [optional] 
**type** | [**ConversationTypeEnum**](ConversationTypeEnum.md) |  | 
**grounding** | [**ConversationGrounding**](ConversationGrounding.md) |  | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_conversation import FlattenedConversation

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedConversation from a JSON string
flattened_conversation_instance = FlattenedConversation.from_json(json)
# print the JSON string representation of the object
print FlattenedConversation.to_json()

# convert the object into a dict
flattened_conversation_dict = flattened_conversation_instance.to_dict()
# create an instance of FlattenedConversation from a dict
flattened_conversation_form_dict = flattened_conversation.from_dict(flattened_conversation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


