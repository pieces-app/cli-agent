# SeededTrackedFormatEvent

Again this is a model designed to be sent over to a context server to be built and then sent along to segment. 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**identifier_description_pair** | [**TrackedFormatEventIdentifierDescriptionPairs**](TrackedFormatEventIdentifierDescriptionPairs.md) |  | 
**format** | [**ReferencedFormat**](ReferencedFormat.md) |  | 
**metadata** | [**TrackedFormatEventMetadata**](TrackedFormatEventMetadata.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_tracked_format_event import SeededTrackedFormatEvent

# TODO update the JSON string below
json = "{}"
# create an instance of SeededTrackedFormatEvent from a JSON string
seeded_tracked_format_event_instance = SeededTrackedFormatEvent.from_json(json)
# print the JSON string representation of the object
print SeededTrackedFormatEvent.to_json()

# convert the object into a dict
seeded_tracked_format_event_dict = seeded_tracked_format_event_instance.to_dict()
# create an instance of SeededTrackedFormatEvent from a dict
seeded_tracked_format_event_form_dict = seeded_tracked_format_event.from_dict(seeded_tracked_format_event_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


