# Classification

This is the specific classification of an Asset's Format.(This is on a per format basis b/c an asset could have different formats that are different format representations of the Asset.)

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**generic** | [**ClassificationGenericEnum**](ClassificationGenericEnum.md) |  | 
**specific** | [**ClassificationSpecificEnum**](ClassificationSpecificEnum.md) |  | 
**rendering** | [**ClassificationRenderingEnum**](ClassificationRenderingEnum.md) |  | [optional] 

## Example

```python
from openapi_client.models.classification import Classification

# TODO update the JSON string below
json = "{}"
# create an instance of Classification from a JSON string
classification_instance = Classification.from_json(json)
# print the JSON string representation of the object
print Classification.to_json()

# convert the object into a dict
classification_dict = classification_instance.to_dict()
# create an instance of Classification from a dict
classification_form_dict = classification.from_dict(classification_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


