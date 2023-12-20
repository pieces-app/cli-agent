# FlattenedAnalysis


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**code** | [**CodeAnalysis**](CodeAnalysis.md) |  | [optional] 
**id** | **str** |  | 
**format** | **str** | this is a reference to the format that it belongs too. | 
**image** | [**FlattenedImageAnalysis**](FlattenedImageAnalysis.md) |  | [optional] 

## Example

```python
from openapi_client.models.flattened_analysis import FlattenedAnalysis

# TODO update the JSON string below
json = "{}"
# create an instance of FlattenedAnalysis from a JSON string
flattened_analysis_instance = FlattenedAnalysis.from_json(json)
# print the JSON string representation of the object
print FlattenedAnalysis.to_json()

# convert the object into a dict
flattened_analysis_dict = flattened_analysis_instance.to_dict()
# create an instance of FlattenedAnalysis from a dict
flattened_analysis_form_dict = flattened_analysis.from_dict(flattened_analysis_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


