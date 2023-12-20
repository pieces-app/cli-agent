# Analyses


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**iterable** | [**List[Analysis]**](Analysis.md) |  | 

## Example

```python
from openapi_client.models.analyses import Analyses

# TODO update the JSON string below
json = "{}"
# create an instance of Analyses from a JSON string
analyses_instance = Analyses.from_json(json)
# print the JSON string representation of the object
print Analyses.to_json()

# convert the object into a dict
analyses_dict = analyses_instance.to_dict()
# create an instance of Analyses from a dict
analyses_form_dict = analyses.from_dict(analyses_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


