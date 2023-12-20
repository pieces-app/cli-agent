# PersonBasicType

This is all optional properties around the most basic information around a non-pieces user.  A Basic type will NOT have a scope as it is not an actual pieces user.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**username** | **str** | username or twitter handle...etc | [optional] 
**name** | **str** | This is the name of the basic user. | [optional] 
**picture** | **str** | this is a url picture representation of a user. | [optional] 
**email** | **str** | an email that was extracted. | [optional] 
**sourced** | [**ExternallySourcedEnum**](ExternallySourcedEnum.md) |  | [optional] 
**url** | **str** | This is a specific url that this basic user came from. | [optional] 
**mailgun** | [**MailgunMetadata**](MailgunMetadata.md) |  | [optional] 

## Example

```python
from openapi_client.models.person_basic_type import PersonBasicType

# TODO update the JSON string below
json = "{}"
# create an instance of PersonBasicType from a JSON string
person_basic_type_instance = PersonBasicType.from_json(json)
# print the JSON string representation of the object
print PersonBasicType.to_json()

# convert the object into a dict
person_basic_type_dict = person_basic_type_instance.to_dict()
# create an instance of PersonBasicType from a dict
person_basic_type_form_dict = person_basic_type.from_dict(person_basic_type_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


