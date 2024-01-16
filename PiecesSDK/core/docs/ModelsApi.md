# openapi_client.ModelsApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**models_create_new_model**](ModelsApi.md#models_create_new_model) | **POST** /models/create | /models/create [POST]
[**models_delete_specific_model**](ModelsApi.md#models_delete_specific_model) | **POST** /models/{model}/delete | /models/{model}/delete [POST]
[**models_snapshot**](ModelsApi.md#models_snapshot) | **GET** /models | /models [GET]
[**unload_models**](ModelsApi.md#unload_models) | **POST** /models/unload | /models/unload [POST]


# **models_create_new_model**
> Model models_create_new_model(seeded_model=seeded_model)

/models/create [POST]



### Example

```python
import time
import os
import openapi_client
from openapi_client.models.model import Model
from openapi_client.models.seeded_model import SeededModel
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
    api_instance = openapi_client.ModelsApi(api_client)
    seeded_model = openapi_client.SeededModel() # SeededModel |  (optional)

    try:
        # /models/create [POST]
        api_response = api_instance.models_create_new_model(seeded_model=seeded_model)
        print("The response of ModelsApi->models_create_new_model:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsApi->models_create_new_model: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **seeded_model** | [**SeededModel**](SeededModel.md)|  | [optional] 

### Return type

[**Model**](Model.md)

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

# **models_delete_specific_model**
> models_delete_specific_model(model)

/models/{model}/delete [POST]



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
    api_instance = openapi_client.ModelsApi(api_client)
    model = 'model_example' # str | model id

    try:
        # /models/{model}/delete [POST]
        api_instance.models_delete_specific_model(model)
    except Exception as e:
        print("Exception when calling ModelsApi->models_delete_specific_model: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **model** | **str**| model id | 

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
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **models_snapshot**
> Models models_snapshot()

/models [GET]

This will get a snapshot of all of your models.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.models import Models
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
    api_instance = openapi_client.ModelsApi(api_client)

    try:
        # /models [GET]
        api_response = api_instance.models_snapshot()
        print("The response of ModelsApi->models_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ModelsApi->models_snapshot: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**Models**](Models.md)

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

# **unload_models**
> unload_models()

/models/unload [POST]

This will unload all of the ml models.

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
    api_instance = openapi_client.ModelsApi(api_client)

    try:
        # /models/unload [POST]
        api_instance.unload_models()
    except Exception as e:
        print("Exception when calling ModelsApi->unload_models: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

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
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

