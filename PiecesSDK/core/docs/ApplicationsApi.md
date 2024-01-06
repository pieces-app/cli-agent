# openapi_client.ApplicationsApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**applications_register**](ApplicationsApi.md#applications_register) | **POST** /applications/register | /applications/register [POST]
[**applications_session_close**](ApplicationsApi.md#applications_session_close) | **POST** /applications/session/close | /applications/session/close [POST]
[**applications_session_open**](ApplicationsApi.md#applications_session_open) | **POST** /applications/session/open | /applications/session/open [POST]
[**applications_session_snapshot**](ApplicationsApi.md#applications_session_snapshot) | **GET** /applications/sessions/{session} | /applications/sessions/{session} [GET]
[**applications_snapshot**](ApplicationsApi.md#applications_snapshot) | **GET** /applications | /applications [GET]
[**applications_specific_application_snapshot**](ApplicationsApi.md#applications_specific_application_snapshot) | **GET** /applications/{application} | /applications/{application} [GET]
[**applications_usage_engagement_interaction**](ApplicationsApi.md#applications_usage_engagement_interaction) | **POST** /applications/usage/engagement/interaction | /applications/usage/engagement/interaction [POST] Scoped to Apps
[**applications_usage_engagement_keyboard**](ApplicationsApi.md#applications_usage_engagement_keyboard) | **POST** /applications/usage/engagement/keyboard | /applications/usage/engagement/keyboard [POST] Scoped to Apps
[**applications_usage_installation**](ApplicationsApi.md#applications_usage_installation) | **POST** /applications/usage/installation | /applications/usage/installation [POST]
[**post_applications_usage_updated**](ApplicationsApi.md#post_applications_usage_updated) | **POST** /applications/usage/updated | /applications/usage/updated [POST]


# **applications_register**
> Application applications_register(application=application)

/applications/register [POST]

This will register a connected applicaiton.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.application import Application
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
    api_instance = openapi_client.ApplicationsApi(api_client)
    application = openapi_client.Application() # Application | This will accept a application. (optional)

    try:
        # /applications/register [POST]
        api_response = api_instance.applications_register(application=application)
        print("The response of ApplicationsApi->applications_register:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_register: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application** | [**Application**](Application.md)| This will accept a application. | [optional] 

### Return type

[**Application**](Application.md)

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

# **applications_session_close**
> Session applications_session_close(body=body)

/applications/session/close [POST]

This will close your opened session! Going to want to accept a session uuid here.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.session import Session
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
    api_instance = openapi_client.ApplicationsApi(api_client)
    body = 'body_example' # str | This will accept a required session uuid. (optional)

    try:
        # /applications/session/close [POST]
        api_response = api_instance.applications_session_close(body=body)
        print("The response of ApplicationsApi->applications_session_close:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_session_close: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body** | **str**| This will accept a required session uuid. | [optional] 

### Return type

[**Session**](Session.md)

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

# **applications_session_open**
> Session applications_session_open()

/applications/session/open [POST]

This will open a new session. A session is when someone is using the pieces application.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.session import Session
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
    api_instance = openapi_client.ApplicationsApi(api_client)

    try:
        # /applications/session/open [POST]
        api_response = api_instance.applications_session_open()
        print("The response of ApplicationsApi->applications_session_open:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_session_open: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**Session**](Session.md)

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

# **applications_session_snapshot**
> Session applications_session_snapshot(session)

/applications/sessions/{session} [GET]

This is an endpoint to get a snapshot of a specific session.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.session import Session
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
    api_instance = openapi_client.ApplicationsApi(api_client)
    session = 'session_example' # str | This is a uuid that points to a session.

    try:
        # /applications/sessions/{session} [GET]
        api_response = api_instance.applications_session_snapshot(session)
        print("The response of ApplicationsApi->applications_session_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_session_snapshot: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **session** | **str**| This is a uuid that points to a session. | 

### Return type

[**Session**](Session.md)

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

# **applications_snapshot**
> Applications applications_snapshot()

/applications [GET]



### Example

```python
import time
import os
import openapi_client
from openapi_client.models.applications import Applications
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
    api_instance = openapi_client.ApplicationsApi(api_client)

    try:
        # /applications [GET]
        api_response = api_instance.applications_snapshot()
        print("The response of ApplicationsApi->applications_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_snapshot: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**Applications**](Applications.md)

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

# **applications_specific_application_snapshot**
> Application applications_specific_application_snapshot(application)

/applications/{application} [GET]

This will retrieve snapshot of a single application.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.application import Application
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
    api_instance = openapi_client.ApplicationsApi(api_client)
    application = 'application_example' # str | This is a uuid that represents an application

    try:
        # /applications/{application} [GET]
        api_response = api_instance.applications_specific_application_snapshot(application)
        print("The response of ApplicationsApi->applications_specific_application_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_specific_application_snapshot: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **application** | **str**| This is a uuid that represents an application | 

### Return type

[**Application**](Application.md)

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

# **applications_usage_engagement_interaction**
> TrackedInteractionEvent applications_usage_engagement_interaction(seeded_tracked_interaction_event=seeded_tracked_interaction_event)

/applications/usage/engagement/interaction [POST] Scoped to Apps

This is an analytics endpoint that will enable us to know when a user engages something via an interaction(ie click/tap).

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.seeded_tracked_interaction_event import SeededTrackedInteractionEvent
from openapi_client.models.tracked_interaction_event import TrackedInteractionEvent
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
    api_instance = openapi_client.ApplicationsApi(api_client)
    seeded_tracked_interaction_event = openapi_client.SeededTrackedInteractionEvent() # SeededTrackedInteractionEvent |  (optional)

    try:
        # /applications/usage/engagement/interaction [POST] Scoped to Apps
        api_response = api_instance.applications_usage_engagement_interaction(seeded_tracked_interaction_event=seeded_tracked_interaction_event)
        print("The response of ApplicationsApi->applications_usage_engagement_interaction:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_usage_engagement_interaction: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **seeded_tracked_interaction_event** | [**SeededTrackedInteractionEvent**](SeededTrackedInteractionEvent.md)|  | [optional] 

### Return type

[**TrackedInteractionEvent**](TrackedInteractionEvent.md)

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

# **applications_usage_engagement_keyboard**
> TrackedKeyboardEvent applications_usage_engagement_keyboard(seeded_tracked_keyboard_event=seeded_tracked_keyboard_event)

/applications/usage/engagement/keyboard [POST] Scoped to Apps

This is an analytics endpoint that will enable us to know when a user uses a keyboard short cut for any sort of engagement.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.seeded_tracked_keyboard_event import SeededTrackedKeyboardEvent
from openapi_client.models.tracked_keyboard_event import TrackedKeyboardEvent
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
    api_instance = openapi_client.ApplicationsApi(api_client)
    seeded_tracked_keyboard_event = openapi_client.SeededTrackedKeyboardEvent() # SeededTrackedKeyboardEvent |  (optional)

    try:
        # /applications/usage/engagement/keyboard [POST] Scoped to Apps
        api_response = api_instance.applications_usage_engagement_keyboard(seeded_tracked_keyboard_event=seeded_tracked_keyboard_event)
        print("The response of ApplicationsApi->applications_usage_engagement_keyboard:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_usage_engagement_keyboard: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **seeded_tracked_keyboard_event** | [**SeededTrackedKeyboardEvent**](SeededTrackedKeyboardEvent.md)|  | [optional] 

### Return type

[**TrackedKeyboardEvent**](TrackedKeyboardEvent.md)

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

# **applications_usage_installation**
> applications_usage_installation(tracked_application_install=tracked_application_install)

/applications/usage/installation [POST]

This is an analytics endpoint that will enable us to know when a user has installed a version of Pieces

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.tracked_application_install import TrackedApplicationInstall
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
    api_instance = openapi_client.ApplicationsApi(api_client)
    tracked_application_install = openapi_client.TrackedApplicationInstall() # TrackedApplicationInstall |  (optional)

    try:
        # /applications/usage/installation [POST]
        api_instance.applications_usage_installation(tracked_application_install=tracked_application_install)
    except Exception as e:
        print("Exception when calling ApplicationsApi->applications_usage_installation: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tracked_application_install** | [**TrackedApplicationInstall**](TrackedApplicationInstall.md)|  | [optional] 

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

# **post_applications_usage_updated**
> post_applications_usage_updated(tracked_application_update=tracked_application_update)

/applications/usage/updated [POST]

This is an endpoint to determine when an application has been updated 

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.tracked_application_update import TrackedApplicationUpdate
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
    api_instance = openapi_client.ApplicationsApi(api_client)
    tracked_application_update = openapi_client.TrackedApplicationUpdate() # TrackedApplicationUpdate | Sending over the previous application version, the current version, and the user. (optional)

    try:
        # /applications/usage/updated [POST]
        api_instance.post_applications_usage_updated(tracked_application_update=tracked_application_update)
    except Exception as e:
        print("Exception when calling ApplicationsApi->post_applications_usage_updated: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **tracked_application_update** | [**TrackedApplicationUpdate**](TrackedApplicationUpdate.md)| Sending over the previous application version, the current version, and the user. | [optional] 

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

