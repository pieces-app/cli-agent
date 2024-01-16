# FlattenedOCRAnalysis

[DAG Safe] Ocr Analysis that will reference FlattenedFormats.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**raw** | [**ReferencedFormat**](ReferencedFormat.md) |  | 
**hocr** | [**ReferencedFormat**](ReferencedFormat.md) |  | 
**model** | [**Model**](Model.md) |  | 
**image** | **str** | this is a refernece to the image analysis. | 

## Example

```python
from openapi_client.models.flattened_ocr_analysis import FlattenedOCRAnalysis

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedOCRAnalysis from a JSON string
flattened_ocr_analysis_instance = FlattenedOCRAnalysis.from_json(json)
# print the JSON string representation of the object
print FlattenedOCRAnalysis.to_json()

# convert the object into a dict
flattened_ocr_analysis_dict = flattened_ocr_analysis_instance.to_dict()
# create an instance of FlattenedOCRAnalysis from a dict
flattened_ocr_analysis_form_dict = flattened_ocr_analysis.from_dict(flattened_ocr_analysis_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


