# TLPCodeSnippetAnalytics


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**statistics** | [**TLPCodeFragmentStatistics**](TLPCodeFragmentStatistics.md) |  | [optional] 
**classification** | [**TLPCodeFragmentClassification**](TLPCodeFragmentClassification.md) |  | [optional] 
**reclassification** | [**TLPCodeFragmentReclassification**](TLPCodeFragmentReclassification.md) |  | [optional] 
**suggested** | [**TLPCodeSnippetSuggestedInteractions**](TLPCodeSnippetSuggestedInteractions.md) |  | [optional] 
**tagify** | [**TLPCodeFragmentTagify**](TLPCodeFragmentTagify.md) |  | [optional] 
**description** | [**TLPCodeFragmentDescription**](TLPCodeFragmentDescription.md) |  | [optional] 

## Example

```python
from openapi_client.models.tlp_code_snippet_analytics import TLPCodeSnippetAnalytics

# TODO update the JSON string below
json = "{}"
# create an instance of TLPCodeSnippetAnalytics from a JSON string
tlp_code_snippet_analytics_instance = TLPCodeSnippetAnalytics.from_json(json)
# print the JSON string representation of the object
print TLPCodeSnippetAnalytics.to_json()

# convert the object into a dict
tlp_code_snippet_analytics_dict = tlp_code_snippet_analytics_instance.to_dict()
# create an instance of TLPCodeSnippetAnalytics from a dict
tlp_code_snippet_analytics_form_dict = tlp_code_snippet_analytics.from_dict(tlp_code_snippet_analytics_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


