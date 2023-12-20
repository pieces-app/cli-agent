# ReferencedDistribution



## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** |  | 
**reference** | [**FlattenedDistribution**](FlattenedDistribution.md) |  | [optional] 

## Example

```python
from openapi_client.models.referenced_distribution import ReferencedDistribution

# TODO update the JSON string below
json = "{}"
# create an instance of ReferencedDistribution from a JSON string
referenced_distribution_instance = ReferencedDistribution.from_json(json)
# print the JSON string representation of the object
print ReferencedDistribution.to_json()

# convert the object into a dict
referenced_distribution_dict = referenced_distribution_instance.to_dict()
# create an instance of ReferencedDistribution from a dict
referenced_distribution_form_dict = referenced_distribution.from_dict(referenced_distribution_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


