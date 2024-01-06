# QGPTStreamInput

This is the input for the /qgpt/stream endpoint.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**relevance** | [**QGPTRelevanceInput**](QGPTRelevanceInput.md) |  | [optional] 
**question** | [**QGPTQuestionInput**](QGPTQuestionInput.md) |  | [optional] 
**request** | **str** | This is an optional Id you can use to identify the result from your request. | [optional] 
**conversation** | **str** | This is the ID of a predefined persisted conversation, if this is not present we will create a new conversation for the input/output.(in the case of a question) | [optional] 
**stop** | **bool** |  | [optional] 

## Example

```python
from openapi_client.models.qgpt_stream_input import QGPTStreamInput

# TODO update the JSON string below
json = "{}"
# create an instance of QGPTStreamInput from a JSON string
qgpt_stream_input_instance = QGPTStreamInput.from_json(json)
# print the JSON string representation of the object
print QGPTStreamInput.to_json()

# convert the object into a dict
qgpt_stream_input_dict = qgpt_stream_input_instance.to_dict()
# create an instance of QGPTStreamInput from a dict
qgpt_stream_input_form_dict = qgpt_stream_input.from_dict(qgpt_stream_input_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


