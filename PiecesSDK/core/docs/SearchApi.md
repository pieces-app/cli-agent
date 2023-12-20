# openapi_client.SearchApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**full_text_search**](SearchApi.md#full_text_search) | **GET** /search/full_text | /search/full_text [GET]
[**neural_code_search**](SearchApi.md#neural_code_search) | **GET** /search/neural_code | /search/neural_code [GET]
[**tag_based_search**](SearchApi.md#tag_based_search) | **POST** /search/tag_based | /search/tag_based [POST]


# **full_text_search**
> SearchedAssets full_text_search(query=query, pseudo=pseudo)

/search/full_text [GET]

This will run FTS for exact search, and will NOT run fuzzy matching. This will only search the content within the 

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.searched_assets import SearchedAssets
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
    api_instance = openapi_client.SearchApi(api_client)
    query = 'query_example' # str | This is a string that you can use to search your assets. (optional)
    pseudo = True # bool | This is helper boolean that will give you the ability to also include your pseudo assets, we will always default to false. (optional)

    try:
        # /search/full_text [GET]
        api_response = api_instance.full_text_search(query=query, pseudo=pseudo)
        print("The response of SearchApi->full_text_search:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SearchApi->full_text_search: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**| This is a string that you can use to search your assets. | [optional] 
 **pseudo** | **bool**| This is helper boolean that will give you the ability to also include your pseudo assets, we will always default to false. | [optional] 

### Return type

[**SearchedAssets**](SearchedAssets.md)

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

# **neural_code_search**
> SearchedAssets neural_code_search(query=query, pseudo=pseudo)

/search/neural_code [GET]

This will run ncs on your assets. This will simply return FlattenedAssets, but will just be the assetuuids that match.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.searched_assets import SearchedAssets
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
    api_instance = openapi_client.SearchApi(api_client)
    query = 'query_example' # str | This is a string that you can use to search your assets. (optional)
    pseudo = True # bool | This is helper boolean that will give you the ability to also include your pseudo assets, we will always default to false. (optional)

    try:
        # /search/neural_code [GET]
        api_response = api_instance.neural_code_search(query=query, pseudo=pseudo)
        print("The response of SearchApi->neural_code_search:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SearchApi->neural_code_search: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query** | **str**| This is a string that you can use to search your assets. | [optional] 
 **pseudo** | **bool**| This is helper boolean that will give you the ability to also include your pseudo assets, we will always default to false. | [optional] 

### Return type

[**SearchedAssets**](SearchedAssets.md)

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

# **tag_based_search**
> SearchedAssets tag_based_search(pseudo=pseudo, seeded_asset_tags=seeded_asset_tags)

/search/tag_based [POST]

This will run our tag based search, and return the assets that best match your passed in tags. This will simply return FlattenedAssets, but will just be the assetuuids that match.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.searched_assets import SearchedAssets
from openapi_client.models.seeded_asset_tags import SeededAssetTags
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
    api_instance = openapi_client.SearchApi(api_client)
    pseudo = True # bool | This is helper boolean that will give you the ability to also include your pseudo assets, we will always default to false. (optional)
    seeded_asset_tags = openapi_client.SeededAssetTags() # SeededAssetTags |  (optional)

    try:
        # /search/tag_based [POST]
        api_response = api_instance.tag_based_search(pseudo=pseudo, seeded_asset_tags=seeded_asset_tags)
        print("The response of SearchApi->tag_based_search:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling SearchApi->tag_based_search: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **pseudo** | **bool**| This is helper boolean that will give you the ability to also include your pseudo assets, we will always default to false. | [optional] 
 **seeded_asset_tags** | [**SeededAssetTags**](SeededAssetTags.md)|  | [optional] 

### Return type

[**SearchedAssets**](SearchedAssets.md)

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

