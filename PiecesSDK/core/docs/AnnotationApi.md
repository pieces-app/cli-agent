# openapi_client.AnnotationApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**annotation_scores_increment**](AnnotationApi.md#annotation_scores_increment) | **POST** /annotation/{annotation}/scores/increment | &#39;/annotation/{annotation}/scores/increment&#39; [POST]
[**annotation_specific_annotation_snapshot**](AnnotationApi.md#annotation_specific_annotation_snapshot) | **GET** /annotation/{annotation} | /annotation/{annotation} [GET]
[**annotation_update**](AnnotationApi.md#annotation_update) | **POST** /annotation/update | /annotation/update [POST]


# **annotation_scores_increment**
> annotation_scores_increment(annotation, seeded_score_increment=seeded_score_increment)

'/annotation/{annotation}/scores/increment' [POST]

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
    api_instance = openapi_client.AnnotationApi(api_client)
    annotation = 'annotation_example' # str | This is a specific annotation uuid.
    seeded_score_increment = openapi_client.SeededScoreIncrement() # SeededScoreIncrement |  (optional)

    try:
        # '/annotation/{annotation}/scores/increment' [POST]
        api_instance.annotation_scores_increment(annotation, seeded_score_increment=seeded_score_increment)
    except Exception as e:
        print("Exception when calling AnnotationApi->annotation_scores_increment: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **annotation** | **str**| This is a specific annotation uuid. | 
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

# **annotation_specific_annotation_snapshot**
> Annotation annotation_specific_annotation_snapshot(annotation)

/annotation/{annotation} [GET]

This will get a snapshot of a specific annotation.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.annotation import Annotation
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
    api_instance = openapi_client.AnnotationApi(api_client)
    annotation = 'annotation_example' # str | This is a specific annotation uuid.

    try:
        # /annotation/{annotation} [GET]
        api_response = api_instance.annotation_specific_annotation_snapshot(annotation)
        print("The response of AnnotationApi->annotation_specific_annotation_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnnotationApi->annotation_specific_annotation_snapshot: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **annotation** | **str**| This is a specific annotation uuid. | 

### Return type

[**Annotation**](Annotation.md)

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

# **annotation_update**
> Annotation annotation_update(annotation=annotation)

/annotation/update [POST]

This will update a specific annotation.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.annotation import Annotation
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
    api_instance = openapi_client.AnnotationApi(api_client)
    annotation = openapi_client.Annotation() # Annotation |  (optional)

    try:
        # /annotation/update [POST]
        api_response = api_instance.annotation_update(annotation=annotation)
        print("The response of AnnotationApi->annotation_update:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling AnnotationApi->annotation_update: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **annotation** | [**Annotation**](Annotation.md)|  | [optional] 

### Return type

[**Annotation**](Annotation.md)

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

