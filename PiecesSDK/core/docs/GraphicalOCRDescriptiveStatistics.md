# GraphicalOCRDescriptiveStatistics

Model for monitoring and evaluating the OCR feature

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**asset** | **str** |  | 
**user** | **str** |  | 
**model** | **str** |  | 
**created** | **str** |  | 
**os** | **str** |  | 
**confidence** | [**GraphicalOCRDescriptiveStatisticsConfidence**](GraphicalOCRDescriptiveStatisticsConfidence.md) |  | 
**duration** | **str** |  | 

## Example

```python
from openapi_client.models.graphical_ocr_descriptive_statistics import GraphicalOCRDescriptiveStatistics

# TODO update the JSON string below
json = "{}"
# create an instance of GraphicalOCRDescriptiveStatistics from a JSON string
graphical_ocr_descriptive_statistics_instance = GraphicalOCRDescriptiveStatistics.from_json(json)
# print the JSON string representation of the object
print GraphicalOCRDescriptiveStatistics.to_json()

# convert the object into a dict
graphical_ocr_descriptive_statistics_dict = graphical_ocr_descriptive_statistics_instance.to_dict()
# create an instance of GraphicalOCRDescriptiveStatistics from a dict
graphical_ocr_descriptive_statistics_form_dict = graphical_ocr_descriptive_statistics.from_dict(graphical_ocr_descriptive_statistics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


