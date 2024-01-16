# FormatMetric

FormatMetric  This is a model that will represent the about of specific formats. ie Generic: 'CODE' specific: 'DART' identifiers: ['FormatUID1, 'FormatUID2']

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**generic** | [**ClassificationGenericEnum**](ClassificationGenericEnum.md) |  | 
**specific** | [**ClassificationSpecificEnum**](ClassificationSpecificEnum.md) |  | 
**identifiers** | **List[str]** | this is a list of format ids | 

## Example

```python
from openapi_client.models.format_metric import FormatMetric

# TODO update the JSON string below
json = "{}"
# create an instance of FormatMetric from a JSON string
format_metric_instance = FormatMetric.from_json(json)
# print the JSON string representation of the object
print FormatMetric.to_json()

# convert the object into a dict
format_metric_dict = format_metric_instance.to_dict()
# create an instance of FormatMetric from a dict
format_metric_form_dict = format_metric.from_dict(format_metric_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


