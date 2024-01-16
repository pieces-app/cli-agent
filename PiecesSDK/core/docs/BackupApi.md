# openapi_client.BackupApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**backup**](BackupApi.md#backup) | **POST** /backup | /backup [POST]
[**backup_asset**](BackupApi.md#backup_asset) | **POST** /backup/asset | /backup/asset [POST]


# **backup**
> backup(assets=assets)

/backup [POST]



### Example

```python
import time
import os
import openapi_client
from openapi_client.models.assets import Assets
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
    api_instance = openapi_client.BackupApi(api_client)
    assets = openapi_client.Assets() # Assets |  (optional)

    try:
        # /backup [POST]
        api_instance.backup(assets=assets)
    except Exception as e:
        print("Exception when calling BackupApi->backup: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **assets** | [**Assets**](Assets.md)|  | [optional] 

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
**505** | HTTP Version Not Supported, This means that your user need to update their local os, or they cannot Backup to the Cloud. |  -  |
**511** | Network Authentication Required, This means that you user needs to be authenticated with OS inorder to backup. The User also need to be connected to their cloud to backup.(If either of the 2 are not connected we will return a 511)  TODO thinking about returning a more comprehensive value for digestion on the recieving side. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **backup_asset**
> backup_asset(asset=asset)

/backup/asset [POST]

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.asset import Asset
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
    api_instance = openapi_client.BackupApi(api_client)
    asset = openapi_client.Asset() # Asset |  (optional)

    try:
        # /backup/asset [POST]
        api_instance.backup_asset(asset=asset)
    except Exception as e:
        print("Exception when calling BackupApi->backup_asset: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **asset** | [**Asset**](Asset.md)|  | [optional] 

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
**505** | HTTP Version Not Supported, This means that your user need to update their local os, or they cannot Backup to the Cloud. |  -  |
**511** | Network Authentication Required, This means that you user needs to be authenticated with OS inorder to backup. The User also need to be connected to their cloud to backup.(If either of the 2 are not connected we will return a 511)  TODO thinking about returning a more comprehensive value for digestion on the recieving side. |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

