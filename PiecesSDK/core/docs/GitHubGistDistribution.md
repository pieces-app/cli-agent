# GitHubGistDistribution

This is a published Github Gist.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**recipients** | [**Recipients**](Recipients.md) |  | 
**public** | **bool** | This will let us know if the gist is public or private. | 
**description** | **str** | This is the description of the Gist Distribution | [optional] 
**name** | **str** | This is the name of the gist you will add. | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**github_id** | **str** | This is the id that github uses to represent the gist. | 
**url** | **str** | This is the url where the gist is. | 

## Example

```python
from openapi_client.models.git_hub_gist_distribution import GitHubGistDistribution

# TODO update the JSON string below
json = "{}"
# create an instance of GitHubGistDistribution from a JSON string
git_hub_gist_distribution_instance = GitHubGistDistribution.from_json(json)
# print the JSON string representation of the object
print GitHubGistDistribution.to_json()

# convert the object into a dict
git_hub_gist_distribution_dict = git_hub_gist_distribution_instance.to_dict()
# create an instance of GitHubGistDistribution from a dict
git_hub_gist_distribution_form_dict = git_hub_gist_distribution.from_dict(git_hub_gist_distribution_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


