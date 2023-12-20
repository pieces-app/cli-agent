# openapi_client.SharesApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**shares_create_new_share**](SharesApi.md#shares_create_new_share) | **POST** /shares/create | /shares/create [POST]
[**shares_delete_share**](SharesApi.md#shares_delete_share) | **POST** /shares/{share}/delete | /shares/{share}/delete [POST]
[**shares_snapshot**](SharesApi.md#shares_snapshot) | **GET** /shares | /shares [GET]
[**shares_specific_share_snapshot**](SharesApi.md#shares_specific_share_snapshot) | **GET** /shares/{share} | /shares/{share} [GET]


# **shares_create_new_share**
> Shares shares_create_new_share(transferables=transferables, seeded_share=seeded_share)

/shares/create [POST]

This endpoint will accept an asset. Response here will be a Share that was created.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.seeded_share import SeededShare
from openapi_client.models.shares import Shares
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
    api_instance = openapi_client.SharesApi(api_client)
    transferables = True # bool | This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) (optional)
    seeded_share = openapi_client.SeededShare() # SeededShare |  (optional)

    try:
        # /shares/create [POST]
        api_response = api_instance.shares_create_new_share(transferables=transferables, seeded_share=seeded_share)
        print("The response of SharesApi->shares_create_new_share:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharesApi->shares_create_new_share: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **transferables** | **bool**| This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) | [optional] 
 **seeded_share** | [**SeededShare**](SeededShare.md)|  | [optional] 

### Return type

[**Shares**](Shares.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **shares_delete_share**
> str shares_delete_share(share)

/shares/{share}/delete [POST]

This endpoint will just take a share id(as a url param) to delete out of the shares table, will return the share id that was deleted.

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
    api_instance = openapi_client.SharesApi(api_client)
    share = 'share_example' # str | Share id

    try:
        # /shares/{share}/delete [POST]
        api_response = api_instance.shares_delete_share(share)
        print("The response of SharesApi->shares_delete_share:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharesApi->shares_delete_share: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **share** | **str**| Share id | 

### Return type

**str**

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

# **shares_snapshot**
> Shares shares_snapshot(transferables=transferables)

/shares [GET]

This will return all of your shares. A Share is an asset that you as a user decided to share with another user via link.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.shares import Shares
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
    api_instance = openapi_client.SharesApi(api_client)
    transferables = True # bool | This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) (optional)

    try:
        # /shares [GET]
        api_response = api_instance.shares_snapshot(transferables=transferables)
        print("The response of SharesApi->shares_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharesApi->shares_snapshot: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **transferables** | **bool**| This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) | [optional] 

### Return type

[**Shares**](Shares.md)

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

# **shares_specific_share_snapshot**
> Share shares_specific_share_snapshot(share, transferables=transferables)

/shares/{share} [GET]

This is an endpoint to enable a client to access a specific share through a provided share id.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.share import Share
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
    api_instance = openapi_client.SharesApi(api_client)
    share = 'share_example' # str | Share id
    transferables = True # bool | This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) (optional)

    try:
        # /shares/{share} [GET]
        api_response = api_instance.shares_specific_share_snapshot(share, transferables=transferables)
        print("The response of SharesApi->shares_specific_share_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SharesApi->shares_specific_share_snapshot: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **share** | **str**| Share id | 
 **transferables** | **bool**| This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) | [optional] 

### Return type

[**Share**](Share.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A specific share per the provided share id. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

