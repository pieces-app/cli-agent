# ImageAnalyses


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**iterable** | [**List[ImageAnalysis]**](ImageAnalysis.md) |  | 

## Example

```python
from openapi_client.models.image_analyses import ImageAnalyses

# TODO update the JSON string below
json = "{}"
# create an instance of ImageAnalyses from a JSON string
image_analyses_instance = ImageAnalyses.from_json(json)
# print the JSON string representation of the object
print ImageAnalyses.to_json()

# convert the object into a dict
image_analyses_dict = image_analyses_instance.to_dict()
# create an instance of ImageAnalyses from a dict
image_analyses_form_dict = image_analyses.from_dict(image_analyses_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


