# FlattenedAnnotation

This is the flattened Version of the annotation, IMPORTANT: when referencing these, ONLY Take the UUID, do NOT polinate(ie w/ asset/person/model) the FlattenedAnnotation as it can create an infinite loop.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | [optional] 
**asset** | [**ReferencedAsset**](ReferencedAsset.md) |  | [optional] 
**person** | [**ReferencedPerson**](ReferencedPerson.md) |  | [optional] 
**type** | [**AnnotationTypeEnum**](AnnotationTypeEnum.md) |  | 
**text** | **str** | This is the text of the annotation. | 
**model** | [**ReferencedModel**](ReferencedModel.md) |  | [optional] 
**pseudo** | **bool** |  | [optional] 
**favorited** | **bool** |  | [optional] 
**anchor** | [**ReferencedAnchor**](ReferencedAnchor.md) |  | [optional] 
**conversation** | [**ReferencedConversation**](ReferencedConversation.md) |  | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 
**messages** | [**FlattenedConversationMessages**](FlattenedConversationMessages.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_annotation import FlattenedAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedAnnotation from a JSON string
flattened_annotation_instance = FlattenedAnnotation.from_json(json)
# print the JSON string representation of the object
print FlattenedAnnotation.to_json()

# convert the object into a dict
flattened_annotation_dict = flattened_annotation_instance.to_dict()
# create an instance of FlattenedAnnotation from a dict
flattened_annotation_form_dict = flattened_annotation.from_dict(flattened_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


