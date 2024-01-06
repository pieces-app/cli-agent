# SeededAnchor


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**type** | [**AnchorTypeEnum**](AnchorTypeEnum.md) |  | 
**watch** | **bool** |  | [optional] 
**fullpath** | **str** |  | 
**asset** | **str** | You may associate a SeededAnchor with an asset | [optional] 
**platform** | [**PlatformEnum**](PlatformEnum.md) |  | [optional] 
**name** | **str** |  | [optional] 
**annotations** | [**List[SeededAnnotation]**](SeededAnnotation.md) |  | [optional] 
**conversation** | **str** |  | [optional] 

## Example

```python
from openapi_client.models.seeded_anchor import SeededAnchor

# TODO update the JSON string below
json = "{}"
# create an instance of SeededAnchor from a JSON string
seeded_anchor_instance = SeededAnchor.from_json(json)
# print the JSON string representation of the object
print SeededAnchor.to_json()

# convert the object into a dict
seeded_anchor_dict = seeded_anchor_instance.to_dict()
# create an instance of SeededAnchor from a dict
seeded_anchor_form_dict = seeded_anchor.from_dict(seeded_anchor_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


