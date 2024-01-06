# openapi_client.ShareApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**share_scores_increment**](ShareApi.md#share_scores_increment) | **POST** /share/{share}/scores/increment | &#39;/share/{share}/scores/increment&#39; [POST]
[**share_snapshot**](ShareApi.md#share_snapshot) | **GET** /share/{share} | /share/{share}
[**share_update**](ShareApi.md#share_update) | **POST** /share/update | /share/update [POST]


# **share_scores_increment**
> share_scores_increment(share, seeded_score_increment=seeded_score_increment)

'/share/{share}/scores/increment' [POST]

This will take in a SeededScoreIncrement and will increment the material relative to the incoming body.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.seeded_score_increment import SeededScoreIncrement
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
    api_instance = openapi_client.ShareApi(api_client)
    share = 'share_example' # str | Share id
    seeded_score_increment = openapi_client.SeededScoreIncrement() # SeededScoreIncrement |  (optional)

    try:
        # '/share/{share}/scores/increment' [POST]
        api_instance.share_scores_increment(share, seeded_score_increment=seeded_score_increment)
    except Exception as e:
        print("Exception when calling ShareApi->share_scores_increment: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **share** | **str**| Share id | 
 **seeded_score_increment** | [**SeededScoreIncrement**](SeededScoreIncrement.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | No Content |  -  |
**500** | Internal Server Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **share_snapshot**
> Share share_snapshot(share, transferables=transferables)

/share/{share}

Get the snapshot of a specific share.

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
    api_instance = openapi_client.ShareApi(api_client)
    share = 'share_example' # str | Share id
    transferables = True # bool | This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) (optional)

    try:
        # /share/{share}
        api_response = api_instance.share_snapshot(share, transferables=transferables)
        print("The response of ShareApi->share_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ShareApi->share_snapshot: %s\n" % e)
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
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **share_update**
> Share share_update(transferables=transferables, share=share)

/share/update [POST]

This endpoint will accept a Share that the user wants to update, and will return a full Share that was updated!

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
    api_instance = openapi_client.ShareApi(api_client)
    transferables = True # bool | This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) (optional)
    share = openapi_client.Share() # Share | This is the Share that needs to be updated. (optional)

    try:
        # /share/update [POST]
        api_response = api_instance.share_update(transferables=transferables, share=share)
        print("The response of ShareApi->share_update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ShareApi->share_update: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **transferables** | **bool**| This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) | [optional] 
 **share** | [**Share**](Share.md)| This is the Share that needs to be updated. | [optional] 

### Return type

[**Share**](Share.md)

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

