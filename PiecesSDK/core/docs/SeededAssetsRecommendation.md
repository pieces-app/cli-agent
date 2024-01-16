# SeededAssetsRecommendation

This is the input data model for the /assets/recommend [GET] endpoint. It includes both a list of assets but also 

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**assets** | [**Assets**](Assets.md) |  | 
**interactions** | [**InteractedAssets**](InteractedAssets.md) |  | 

## Example

```python
from openapi_client.models.seeded_assets_recommendation import SeededAssetsRecommendation

# TODO update the JSON string below
json = "{}"
# create an instance of SeededAssetsRecommendation from a JSON string
seeded_assets_recommendation_instance = SeededAssetsRecommendation.from_json(json)
# print the JSON string representation of the object
print SeededAssetsRecommendation.to_json()

# convert the object into a dict
seeded_assets_recommendation_dict = seeded_assets_recommendation_instance.to_dict()
# create an instance of SeededAssetsRecommendation from a dict
seeded_assets_recommendation_form_dict = seeded_assets_recommendation.from_dict(seeded_assets_recommendation_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


