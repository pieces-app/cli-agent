# SeededDistribution

TODO if we add another distribution add to this, Distribution, and flattenedDistribution.  can only use this Model with our Linkify Model.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**mailgun** | [**MailgunDistribution**](MailgunDistribution.md) |  | [optional] 
**github** | [**SeededGitHubDistribution**](SeededGitHubDistribution.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_distribution import SeededDistribution

# TODO update the JSON string below
json = "{}"
# create an instance of SeededDistribution from a JSON string
seeded_distribution_instance = SeededDistribution.from_json(json)
# print the JSON string representation of the object
print SeededDistribution.to_json()

# convert the object into a dict
seeded_distribution_dict = seeded_distribution_instance.to_dict()
# create an instance of SeededDistribution from a dict
seeded_distribution_form_dict = seeded_distribution.from_dict(seeded_distribution_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


