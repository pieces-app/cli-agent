# Distribution

This is a fully referenced version of a Distribution. TODO add additional distributions such as slack, google_chat, ...etc

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**share** | [**FlattenedShare**](FlattenedShare.md) |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**updated** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**deleted** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | [optional] 
**mailgun** | [**MailgunDistribution**](MailgunDistribution.md) |  | [optional] 
**github** | [**GitHubDistribution**](GitHubDistribution.md) |  | [optional] 

## Example

```python
from openapi_client.models.distribution import Distribution

# TODO update the JSON string below
json = "{}"
# create an instance of Distribution from a JSON string
distribution_instance = Distribution.from_json(json)
# print the JSON string representation of the object
print Distribution.to_json()

# convert the object into a dict
distribution_dict = distribution_instance.to_dict()
# create an instance of Distribution from a dict
distribution_form_dict = distribution.from_dict(distribution_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


