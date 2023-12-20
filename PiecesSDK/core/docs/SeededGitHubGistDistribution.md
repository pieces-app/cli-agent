# SeededGitHubGistDistribution

This is the minimum information needed to distribute a Piece to a Gist.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**recipients** | [**Recipients**](Recipients.md) |  | [optional] 
**public** | **bool** | we will default to true | [optional] 
**description** | **str** | This is the description of the Gist Distribution | [optional] 
**name** | **str** | This is the name of the gist you will add. | 

## Example

```python
from openapi_client.models.seeded_git_hub_gist_distribution import SeededGitHubGistDistribution

# TODO update the JSON string below
json = "{}"
# create an instance of SeededGitHubGistDistribution from a JSON string
seeded_git_hub_gist_distribution_instance = SeededGitHubGistDistribution.from_json(json)
# print the JSON string representation of the object
print SeededGitHubGistDistribution.to_json()

# convert the object into a dict
seeded_git_hub_gist_distribution_dict = seeded_git_hub_gist_distribution_instance.to_dict()
# create an instance of SeededGitHubGistDistribution from a dict
seeded_git_hub_gist_distribution_form_dict = seeded_git_hub_gist_distribution.from_dict(seeded_git_hub_gist_distribution_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


