# openapi_client.FormatsApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**formats_snapshot**](FormatsApi.md#formats_snapshot) | **GET** /formats | /formats [GET] Scoped to Formats
[**formats_specific_format_snapshot**](FormatsApi.md#formats_specific_format_snapshot) | **GET** /formats/{format} | /formats/{format} [GET] Scoped to Formats


# **formats_snapshot**
> Formats formats_snapshot(transferables=transferables)

/formats [GET] Scoped to Formats

Get all of your formats for a given user.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.formats import Formats
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:3000
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:3000"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.FormatsApi(api_client)
    transferables = True # bool | This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) (optional)

    try:
        # /formats [GET] Scoped to Formats
        api_response = api_instance.formats_snapshot(transferables=transferables)
        print("The response of FormatsApi->formats_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormatsApi->formats_snapshot: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **transferables** | **bool**| This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) | [optional] 

### Return type

[**Formats**](Formats.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **formats_specific_format_snapshot**
> Format formats_specific_format_snapshot(format, transferable=transferable)

/formats/{format} [GET] Scoped to Formats

Request a specific format when given a id (uuid in path params)

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.format import Format
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:3000
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:3000"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.FormatsApi(api_client)
    format = '102ff265-fdfb-4142-8d94-4932d400199c' # str | The id (uuid) for a specific format.
    transferable = True # bool | This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) (optional)

    try:
        # /formats/{format} [GET] Scoped to Formats
        api_response = api_instance.formats_specific_format_snapshot(format, transferable=transferable)
        print("The response of FormatsApi->formats_specific_format_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling FormatsApi->formats_specific_format_snapshot: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **format** | **str**| The id (uuid) for a specific format. | 
 **transferable** | **bool**| This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) | [optional] 

### Return type

[**Format**](Format.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

