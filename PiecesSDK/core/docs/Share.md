# Share

This represents what information that is relavent to anything and every sharing related. v1 will look very bare and will add more and more data as we go!  if user is undefined && access is public then we have an asset that is publicly available.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**id** | **str** | This is the uuid that represents this share model. | 
**user** | **str** | this is the uuid of the user that the share is created for. | [optional] 
**asset** | [**FlattenedAsset**](FlattenedAsset.md) |  | [optional] 
**assets** | [**FlattenedAssets**](FlattenedAssets.md) |  | [optional] 
**link** | **str** | This is the prebuilt link. | 
**access** | [**AccessEnum**](AccessEnum.md) |  | 
**accessors** | [**Accessors**](Accessors.md) |  | 
**created** | [**GroupedTimestamp**](GroupedTimestamp.md) |  | 
**short** | **str** | This is a shortened version of our uuid. | 
**name** | **str** | this is an optional name we can give to the link, ie ?p&#x3D;JAVASCRIPT or what ever the user wants as long as it is available. | [optional] 
**distributions** | [**Distributions**](Distributions.md) |  | [optional] 
**score** | [**Score**](Score.md) |  | [optional] 

## Example

```python
from openapi_client.models.share import Share

# TODO update the JSON string below
json = "{}"
# create an instance of Share from a JSON string
share_instance = Share.from_json(json)
# print the JSON string representation of the object
print Share.to_json()

# convert the object into a dict
share_dict = share_instance.to_dict()
# create an instance of Share from a dict
share_form_dict = share.from_dict(share_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


