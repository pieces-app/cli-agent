# SeededFormat

This is seeded data that will be come a format.  We will throw an Error if, 1) file and fragment are both defined, 2) file and fragment are both null.  if this is being used within the /assets/create endpoint or the /{application}/create endpoint, we will not take the classificaiton into account, as it is only used in the syntax highlighting related endpoints.That being said if you do want to override your classification, please look at the metadata within the file or the fragment.

## Properties
Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**var_schema** | [**EmbeddedModelSchema**](EmbeddedModelSchema.md) |  | [optional] 
**file** | [**SeededFile**](SeededFile.md) |  | [optional] 
**fragment** | [**SeededFragment**](SeededFragment.md) |  | [optional] 
**classification** | [**SeededClassification**](SeededClassification.md) |  | [optional] 

## Example

```python
from openapi_client.models.seeded_format import SeededFormat

# TODO update the JSON string below
json = "{}"
# create an instance of SeededFormat from a JSON string
seeded_format_instance = SeededFormat.from_json(json)
# print the JSON string representation of the object
print SeededFormat.to_json()

# convert the object into a dict
seeded_format_dict = seeded_format_instance.to_dict()
# create an instance of SeededFormat from a dict
seeded_format_form_dict = seeded_format.from_dict(seeded_format_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


