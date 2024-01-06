# openapi_client.WebsitesApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**websites_create_new_website**](WebsitesApi.md#websites_create_new_website) | **POST** /websites/create | /websites/create [POST]
[**websites_delete_specific_website**](WebsitesApi.md#websites_delete_specific_website) | **POST** /websites/{website}/delete | /websites/{website}/delete [POST]
[**websites_exists**](WebsitesApi.md#websites_exists) | **POST** /websites/exists | /websites/exists [POST]
[**websites_snapshot**](WebsitesApi.md#websites_snapshot) | **GET** /websites | /websites [GET]


# **websites_create_new_website**
> Website websites_create_new_website(transferables=transferables, seeded_website=seeded_website)

/websites/create [POST]

This will create a website and attach it to a specific asset.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.seeded_website import SeededWebsite
from openapi_client.models.website import Website
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
    api_instance = openapi_client.WebsitesApi(api_client)
    transferables = True # bool | This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) (optional)
    seeded_website = openapi_client.SeededWebsite() # SeededWebsite |  (optional)

    try:
        # /websites/create [POST]
        api_response = api_instance.websites_create_new_website(transferables=transferables, seeded_website=seeded_website)
        print("The response of WebsitesApi->websites_create_new_website:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebsitesApi->websites_create_new_website: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **transferables** | **bool**| This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) | [optional] 
 **seeded_website** | [**SeededWebsite**](SeededWebsite.md)|  | [optional] 

### Return type

[**Website**](Website.md)

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

# **websites_delete_specific_website**
> websites_delete_specific_website(website)

/websites/{website}/delete [POST]

This will delete a specific website!

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
    api_instance = openapi_client.WebsitesApi(api_client)
    website = 'website_example' # str | website id

    try:
        # /websites/{website}/delete [POST]
        api_instance.websites_delete_specific_website(website)
    except Exception as e:
        print("Exception when calling WebsitesApi->websites_delete_specific_website: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **website** | **str**| website id | 

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

# **websites_exists**
> ExistingMetadata websites_exists(existent_metadata=existent_metadata)

/websites/exists [POST]

This will check all of the websites in our database to see if this specific provided website actually exists, if not we will just return a null website in the output.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.existent_metadata import ExistentMetadata
from openapi_client.models.existing_metadata import ExistingMetadata
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
    api_instance = openapi_client.WebsitesApi(api_client)
    existent_metadata = openapi_client.ExistentMetadata() # ExistentMetadata |  (optional)

    try:
        # /websites/exists [POST]
        api_response = api_instance.websites_exists(existent_metadata=existent_metadata)
        print("The response of WebsitesApi->websites_exists:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebsitesApi->websites_exists: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **existent_metadata** | [**ExistentMetadata**](ExistentMetadata.md)|  | [optional] 

### Return type

[**ExistingMetadata**](ExistingMetadata.md)

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

# **websites_snapshot**
> Websites websites_snapshot(transferables=transferables)

/websites [GET]

This will get a snapshot of all your websites.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.websites import Websites
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
    api_instance = openapi_client.WebsitesApi(api_client)
    transferables = True # bool | This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) (optional)

    try:
        # /websites [GET]
        api_response = api_instance.websites_snapshot(transferables=transferables)
        print("The response of WebsitesApi->websites_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WebsitesApi->websites_snapshot: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **transferables** | **bool**| This is a boolean that will decided if we are want to return the transferable data (default) or not(performance enhancement) | [optional] 

### Return type

[**Websites**](Websites.md)

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

