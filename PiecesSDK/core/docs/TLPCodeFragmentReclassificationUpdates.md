# TLPCodeFragmentReclassificationUpdates


## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**previous** | [**Classification**](Classification.md) |  | 
**current** | [**Classification**](Classification.md) |  | 

## Example

```python
from openapi_client.models.tlp_code_fragment_reclassification_updates import TLPCodeFragmentReclassificationUpdates

# TODO update the JSON string below
json = "{}"
# create an instance of TLPCodeFragmentReclassificationUpdates from a JSON string
tlp_code_fragment_reclassification_updates_instance = TLPCodeFragmentReclassificationUpdates.from_json(json)
# print the JSON string representation of the object
print TLPCodeFragmentReclassificationUpdates.to_json()

# convert the object into a dict
tlp_code_fragment_reclassification_updates_dict = tlp_code_fragment_reclassification_updates_instance.to_dict()
# create an instance of TLPCodeFragmentReclassificationUpdates from a dict
tlp_code_fragment_reclassification_updates_form_dict = tlp_code_fragment_reclassification_updates.from_dict(tlp_code_fragment_reclassification_updates_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


