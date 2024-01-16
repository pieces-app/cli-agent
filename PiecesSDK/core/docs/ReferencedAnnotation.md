# ReferencedAnnotation

This is the referenced version of a annotation, main used for the uuid.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**reference** | [**FlattenedAnnotation**](FlattenedAnnotation.md) |  | [optional] 

## Example

```python
from openapi_client.models.referenced_annotation import ReferencedAnnotation

# TODO update the JSON string below
json = "{}"
# create an instance of ReferencedAnnotation from a JSON string
referenced_annotation_instance = ReferencedAnnotation.from_json(json)
# print the JSON string representation of the object
print ReferencedAnnotation.to_json()

# convert the object into a dict
referenced_annotation_dict = referenced_annotation_instance.to_dict()
# create an instance of ReferencedAnnotation from a dict
referenced_annotation_form_dict = referenced_annotation.from_dict(referenced_annotation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


