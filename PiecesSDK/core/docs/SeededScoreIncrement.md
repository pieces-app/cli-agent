# SeededScoreIncrement

This is the body for a respective scores increment,  This will enable us to know what material we want to increment, all of which are optional, if it is defined we will attempt to increment the material.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**asset** | [**SeededScore**](SeededScore.md) |  | [optional] 
**assets** | [**SeededScore**](SeededScore.md) |  | [optional] 
**website** | [**SeededScore**](SeededScore.md) |  | [optional] 
**websites** | [**SeededScore**](SeededScore.md) |  | [optional] 
**anchor** | [**SeededScore**](SeededScore.md) |  | [optional] 
**anchors** | [**SeededScore**](SeededScore.md) |  | [optional] 
**anchor_point** | [**SeededScore**](SeededScore.md) |  | [optional] 
**anchor_points** | [**SeededScore**](SeededScore.md) |  | [optional] 
**annotation** | [**SeededScore**](SeededScore.md) |  | [optional] 
**annotations** | [**SeededScore**](SeededScore.md) |  | [optional] 
**conversation** | [**SeededScore**](SeededScore.md) |  | [optional] 
**conversations** | [**SeededScore**](SeededScore.md) |  | [optional] 
**conversation_message** | [**SeededScore**](SeededScore.md) |  | [optional] 
**conversation_messages** | [**SeededScore**](SeededScore.md) |  | [optional] 
**share** | [**SeededScore**](SeededScore.md) |  | [optional] 
**shares** | [**SeededScore**](SeededScore.md) |  | [optional] 
**sensitive** | [**SeededScore**](SeededScore.md) |  | [optional] 
**sensitives** | [**SeededScore**](SeededScore.md) |  | [optional] 
**hint** | [**SeededScore**](SeededScore.md) |  | [optional] 
**hints** | [**SeededScore**](SeededScore.md) |  | [optional] 
**person** | [**SeededScore**](SeededScore.md) |  | [optional] 
**persons** | [**SeededScore**](SeededScore.md) |  | [optional] 
**tag** | [**SeededScore**](SeededScore.md) |  | [optional] 
**tags** | [**SeededScore**](SeededScore.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_score_increment import SeededScoreIncrement

# TODO update the JSON string below
json = "{}"
# create an instance of SeededScoreIncrement from a JSON string
seeded_score_increment_instance = SeededScoreIncrement.from_json(json)
# print the JSON string representation of the object
print SeededScoreIncrement.to_json()

# convert the object into a dict
seeded_score_increment_dict = seeded_score_increment_instance.to_dict()
# create an instance of SeededScoreIncrement from a dict
seeded_score_increment_form_dict = seeded_score_increment.from_dict(seeded_score_increment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


