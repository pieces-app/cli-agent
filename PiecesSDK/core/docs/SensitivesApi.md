# openapi_client.SensitivesApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**sensitives_create_new_sensitive**](SensitivesApi.md#sensitives_create_new_sensitive) | **POST** /sensitives/create | /sensitives/create [POST]
[**sensitives_delete_sensitive**](SensitivesApi.md#sensitives_delete_sensitive) | **POST** /sensitives/{sensitive}/delete | /sensitives/{sensitive}/delete [POST]
[**sensitives_snapshot**](SensitivesApi.md#sensitives_snapshot) | **GET** /sensitives | /sensitives [GET]


# **sensitives_create_new_sensitive**
> Sensitive sensitives_create_new_sensitive(seeded_sensitive=seeded_sensitive)

/sensitives/create [POST]

This will create a new sensitive model.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.seeded_sensitive import SeededSensitive
from openapi_client.models.sensitive import Sensitive
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
    api_instance = openapi_client.SensitivesApi(api_client)
    seeded_sensitive = openapi_client.SeededSensitive() # SeededSensitive |  (optional)

    try:
        # /sensitives/create [POST]
        api_response = api_instance.sensitives_create_new_sensitive(seeded_sensitive=seeded_sensitive)
        print("The response of SensitivesApi->sensitives_create_new_sensitive:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SensitivesApi->sensitives_create_new_sensitive: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **seeded_sensitive** | [**SeededSensitive**](SeededSensitive.md)|  | [optional] 

### Return type

[**Sensitive**](Sensitive.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sensitives_delete_sensitive**
> sensitives_delete_sensitive(sensitive)

/sensitives/{sensitive}/delete [POST]

This will delete a sensitive based on the sensitive uuid.

### Example

```python
import time
import os
import openapi_client
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
    api_instance = openapi_client.SensitivesApi(api_client)
    sensitive = 'sensitive_example' # str | This is a uuid that represents a sensitive.

    try:
        # /sensitives/{sensitive}/delete [POST]
        api_instance.sensitives_delete_sensitive(sensitive)
    except Exception as e:
        print("Exception when calling SensitivesApi->sensitives_delete_sensitive: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sensitive** | **str**| This is a uuid that represents a sensitive. | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | No Content |  -  |
**500** |  |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **sensitives_snapshot**
> Sensitives sensitives_snapshot()

/sensitives [GET]

This will get a snapshot of all of the sensitives.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.sensitives import Sensitives
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
    api_instance = openapi_client.SensitivesApi(api_client)

    try:
        # /sensitives [GET]
        api_response = api_instance.sensitives_snapshot()
        print("The response of SensitivesApi->sensitives_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SensitivesApi->sensitives_snapshot: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**Sensitives**](Sensitives.md)

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

