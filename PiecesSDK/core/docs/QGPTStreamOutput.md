# QGPTStreamOutput

This is the out for the /qgpt/stream endpoint.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**request** | **str** | This is the id used to represent the stream of response. this will always be present. We will use the value passed inby the client, or we will generate one. | [optional] 
**relevance** | [**QGPTRelevanceOutput**](QGPTRelevanceOutput.md) |  | [optional] 
**question** | [**QGPTQuestionOutput**](QGPTQuestionOutput.md) |  | [optional] 
**status** | [**QGPTStreamEnum**](QGPTStreamEnum.md) |  | [optional] 
**conversation** | **str** | This is the ID of a predefined persisted conversation, if this is not present we will create a new conversation for the input/output.(in the case of a question) | 

## Example

```python
from openapi_client.models.qgpt_stream_output import QGPTStreamOutput

# TODO update the JSON string below
json = "{}"
# create an instance of QGPTStreamOutput from a JSON string
qgpt_stream_output_instance = QGPTStreamOutput.from_json(json)
# print the JSON string representation of the object
print QGPTStreamOutput.to_json()

# convert the object into a dict
qgpt_stream_output_dict = qgpt_stream_output_instance.to_dict()
# create an instance of QGPTStreamOutput from a dict
qgpt_stream_output_form_dict = qgpt_stream_output.from_dict(qgpt_stream_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


