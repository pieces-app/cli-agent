# SeededClassification

This is the specific classification of an Asset's Format.(This is on a per format basis b/c an asset could have different formats that are different format representations of the Asset.)

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**generic** | [**ClassificationGenericEnum**](ClassificationGenericEnum.md) |  | [optional] 
**specific** | [**ClassificationSpecificEnum**](ClassificationSpecificEnum.md) |  | [optional] 
**rendering** | [**ClassificationRenderingEnum**](ClassificationRenderingEnum.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_classification import SeededClassification

# TODO update the JSON string below
json = "{}"
# create an instance of SeededClassification from a JSON string
seeded_classification_instance = SeededClassification.from_json(json)
# print the JSON string representation of the object
print SeededClassification.to_json()

# convert the object into a dict
seeded_classification_dict = seeded_classification_instance.to_dict()
# create an instance of SeededClassification from a dict
seeded_classification_form_dict = seeded_classification.from_dict(seeded_classification_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


