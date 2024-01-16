# QGPTRepromptOutput


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**query** | **str** |  | 

## Example

```python
from openapi_client.models.qgpt_reprompt_output import QGPTRepromptOutput

# TODO update the JSON string below
json = "{}"
# create an instance of QGPTRepromptOutput from a JSON string
qgpt_reprompt_output_instance = QGPTRepromptOutput.from_json(json)
# print the JSON string representation of the object
print QGPTRepromptOutput.to_json()

# convert the object into a dict
qgpt_reprompt_output_dict = qgpt_reprompt_output_instance.to_dict()
# create an instance of QGPTRepromptOutput from a dict
qgpt_reprompt_output_form_dict = qgpt_reprompt_output.from_dict(qgpt_reprompt_output_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


