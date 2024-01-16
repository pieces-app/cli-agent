# TLPCodeProcessing


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**fragment** | [**TLPCodeSnippetAnalytics**](TLPCodeSnippetAnalytics.md) |  | [optional] 
**file** | [**TLPCodeFileAnalytics**](TLPCodeFileAnalytics.md) |  | [optional] 
**directory** | [**TLPCodeDirectoryAnalytics**](TLPCodeDirectoryAnalytics.md) |  | [optional] 
**repository** | [**TLPCodeRepositoryAnalytics**](TLPCodeRepositoryAnalytics.md) |  | [optional] 

## Example

```python
from openapi_client.models.tlp_code_processing import TLPCodeProcessing

# TODO update the JSON string below
json = "{}"
# create an instance of TLPCodeProcessing from a JSON string
tlp_code_processing_instance = TLPCodeProcessing.from_json(json)
# print the JSON string representation of the object
print TLPCodeProcessing.to_json()

# convert the object into a dict
tlp_code_processing_dict = tlp_code_processing_instance.to_dict()
# create an instance of TLPCodeProcessing from a dict
tlp_code_processing_form_dict = tlp_code_processing.from_dict(tlp_code_processing_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


