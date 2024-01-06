# QGPTRelevanceInputOptions


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**database** | **bool** | This is an optional boolen that will tell us to use our entire snippet database as the sample. | [optional] 
**question** | **bool** | This is an optional boolean, that will let the serve know if you want to combine the 2 endpointsboth relevance &amp;&amp; the Question endpoint to return the final results. | [optional] 

## Example

```python
from openapi_client.models.qgpt_relevance_input_options import QGPTRelevanceInputOptions

# TODO update the JSON string below
json = "{}"
# create an instance of QGPTRelevanceInputOptions from a JSON string
qgpt_relevance_input_options_instance = QGPTRelevanceInputOptions.from_json(json)
# print the JSON string representation of the object
print QGPTRelevanceInputOptions.to_json()

# convert the object into a dict
qgpt_relevance_input_options_dict = qgpt_relevance_input_options_instance.to_dict()
# create an instance of QGPTRelevanceInputOptions from a dict
qgpt_relevance_input_options_form_dict = qgpt_relevance_input_options.from_dict(qgpt_relevance_input_options_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


