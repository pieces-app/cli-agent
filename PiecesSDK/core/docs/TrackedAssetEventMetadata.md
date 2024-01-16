# TrackedAssetEventMetadata


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**reclassification** | [**TrackedAssetEventFormatReclassificationMetadata**](TrackedAssetEventFormatReclassificationMetadata.md) |  | [optional] 
**creation** | [**TrackedAssetEventCreationMetadata**](TrackedAssetEventCreationMetadata.md) |  | [optional] 
**rename** | [**TrackedAssetEventRenameMetadata**](TrackedAssetEventRenameMetadata.md) |  | [optional] 
**tag** | [**ReferencedTag**](ReferencedTag.md) |  | [optional] 
**website** | [**ReferencedWebsite**](ReferencedWebsite.md) |  | [optional] 
**person** | [**ReferencedPerson**](ReferencedPerson.md) |  | [optional] 
**sensitive** | [**ReferencedSensitive**](ReferencedSensitive.md) |  | [optional] 
**share** | [**ReferencedShare**](ReferencedShare.md) |  | [optional] 
**search** | [**TrackedAssetsEventSearchMetadata**](TrackedAssetsEventSearchMetadata.md) |  | [optional] 
**annotation** | [**ReferencedAnnotation**](ReferencedAnnotation.md) |  | [optional] 
**hint** | [**ReferencedHint**](ReferencedHint.md) |  | [optional] 
**anchor** | [**ReferencedAnchor**](ReferencedAnchor.md) |  | [optional] 

## Example

```python
from openapi_client.models.tracked_asset_event_metadata import TrackedAssetEventMetadata

# TODO update the JSON string below
json = "{}"
# create an instance of TrackedAssetEventMetadata from a JSON string
tracked_asset_event_metadata_instance = TrackedAssetEventMetadata.from_json(json)
# print the JSON string representation of the object
print TrackedAssetEventMetadata.to_json()

# convert the object into a dict
tracked_asset_event_metadata_dict = tracked_asset_event_metadata_instance.to_dict()
# create an instance of TrackedAssetEventMetadata from a dict
tracked_asset_event_metadata_form_dict = tracked_asset_event_metadata.from_dict(tracked_asset_event_metadata_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


