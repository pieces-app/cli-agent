# SeededAnnotation

This is the percursor to a fully referenced Annotation.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**mechanism** | [**MechanismEnum**](MechanismEnum.md) |  | [optional] 
**asset** | **str** |  | [optional] 
**person** | **str** |  | [optional] 
**type** | [**AnnotationTypeEnum**](AnnotationTypeEnum.md) |  | 
**text** | **str** | This is the text of the annotation. | 
**model** | **str** |  | [optional] 
**pseudo** | **bool** |  | [optional] 
**favorited** | **bool** |  | [optional] 
**anchor** | **str** |  | [optional] 
**conversation** | **str** |  | [optional] 
**messages** | [**FlattenedConversationMessages**](FlattenedConversationMessages.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_annotation import SeededAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of SeededAnnotation from a JSON string
seeded_annotation_instance = SeededAnnotation.from_json(json)
# print the JSON string representation of the object
print SeededAnnotation.to_json()

# convert the object into a dict
seeded_annotation_dict = seeded_annotation_instance.to_dict()
# create an instance of SeededAnnotation from a dict
seeded_annotation_form_dict = seeded_annotation.from_dict(seeded_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


