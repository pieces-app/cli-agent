# openapi_client.NotificationsApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**send_local_notification**](NotificationsApi.md#send_local_notification) | **POST** /notifications/local/send | Send notification


# **send_local_notification**
> send_local_notification(notification=notification)

Send notification

This one is to universaly send notifications from any member of the system

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.notification import Notification
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
    api_instance = openapi_client.NotificationsApi(api_client)
    notification = openapi_client.Notification() # Notification |  (optional)

    try:
        # Send notification
        api_instance.send_local_notification(notification=notification)
    except Exception as e:
        print("Exception when calling NotificationsApi->send_local_notification: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **notification** | [**Notification**](Notification.md)|  | [optional] 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: Not defined

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

