# Analysis

This the the MlAnalysis Object, that will go on a format.  this will hold all the different analysis models!  ** keep format just a uuid for now **

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**code** | [**CodeAnalysis**](CodeAnalysis.md) |  | [optional] 
**id** | **str** |  | 
**format** | **str** | this is a reference to the format that it belongs too. | 
**image** | [**ImageAnalysis**](ImageAnalysis.md) |  | [optional] 

## Example

```python
from openapi_client.models.analysis import Analysis

# TODO update the JSON string below
json = "{}"
# create an instance of Analysis from a JSON string
analysis_instance = Analysis.from_json(json)
# print the JSON string representation of the object
print Analysis.to_json()

# convert the object into a dict
analysis_dict = analysis_instance.to_dict()
# create an instance of Analysis from a dict
analysis_form_dict = analysis.from_dict(analysis_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


