# openapi_client.RelationshipsApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**relationships_snapshot**](RelationshipsApi.md#relationships_snapshot) | **GET** /relationships | /relationships [GET]


# **relationships_snapshot**
> Relationships relationships_snapshot()

/relationships [GET]

This will reurn all of the relationships that exists within your pieces db.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.relationships import Relationships
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
    api_instance = openapi_client.RelationshipsApi(api_client)

    try:
        # /relationships [GET]
        api_response = api_instance.relationships_snapshot()
        print("The response of RelationshipsApi->relationships_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RelationshipsApi->relationships_snapshot: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**Relationships**](Relationships.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

