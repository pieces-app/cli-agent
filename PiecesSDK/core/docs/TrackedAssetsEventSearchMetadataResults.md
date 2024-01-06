# TrackedAssetsEventSearchMetadataResults

Numbers related to search results

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**fuzzy** | **float** | Total number of fuzzy results | [optional] 
**exact** | **float** | Total number of exact results | [optional] 
**assets** | [**FlattenedAssets**](FlattenedAssets.md) |  | [optional] 
**space** | [**Space**](Space.md) |  | [optional] 

## Example

```python
from openapi_client.models.tracked_assets_event_search_metadata_results import TrackedAssetsEventSearchMetadataResults

# TODO update the JSON string below
json = "{}"
# create an instance of TrackedAssetsEventSearchMetadataResults from a JSON string
tracked_assets_event_search_metadata_results_instance = TrackedAssetsEventSearchMetadataResults.from_json(json)
# print the JSON string representation of the object
print TrackedAssetsEventSearchMetadataResults.to_json()

# convert the object into a dict
tracked_assets_event_search_metadata_results_dict = tracked_assets_event_search_metadata_results_instance.to_dict()
# create an instance of TrackedAssetsEventSearchMetadataResults from a dict
tracked_assets_event_search_metadata_results_form_dict = tracked_assets_event_search_metadata_results.from_dict(tracked_assets_event_search_metadata_results_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


