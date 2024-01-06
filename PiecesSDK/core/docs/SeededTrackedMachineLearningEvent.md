# SeededTrackedMachineLearningEvent


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**tlp** | [**TLPMachineLearningProcessingEvent**](TLPMachineLearningProcessingEvent.md) |  | [optional] 
**graphical** | [**GraphicalMachineLearningProcessingEvent**](GraphicalMachineLearningProcessingEvent.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_tracked_machine_learning_event import SeededTrackedMachineLearningEvent

# TODO update the JSON string below
json = "{}"
# create an instance of SeededTrackedMachineLearningEvent from a JSON string
seeded_tracked_machine_learning_event_instance = SeededTrackedMachineLearningEvent.from_json(json)
# print the JSON string representation of the object
print SeededTrackedMachineLearningEvent.to_json()

# convert the object into a dict
seeded_tracked_machine_learning_event_dict = seeded_tracked_machine_learning_event_instance.to_dict()
# create an instance of SeededTrackedMachineLearningEvent from a dict
seeded_tracked_machine_learning_event_form_dict = seeded_tracked_machine_learning_event.from_dict(seeded_tracked_machine_learning_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


