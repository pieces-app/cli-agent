# openapi_client.UsersApi

All URIs are relative to *http://localhost:3000*

Method | HTTP request | Description
------------- | ------------- | -------------
[**authenticate_from_oauth_token**](UsersApi.md#authenticate_from_oauth_token) | **POST** /users/authenticate/from_token | /users/authenticate/from_token [POST]
[**users_disconnect_user**](UsersApi.md#users_disconnect_user) | **POST** /users/{user}/disconnect | /users/{user}/disconnect [POST]
[**users_snapshot**](UsersApi.md#users_snapshot) | **GET** /users | /users [GET]
[**users_specific_user_snapshot**](UsersApi.md#users_specific_user_snapshot) | **GET** /users/{user} | /users/{user} [GET] Scoped to Users


# **authenticate_from_oauth_token**
> UserProfile authenticate_from_oauth_token(o_auth_token=o_auth_token)

/users/authenticate/from_token [POST]

Creates a User From a oAuth Token

### Example

* OAuth Authentication (auth0):
* OAuth Authentication (auth0):
* OAuth Authentication (auth0):
```python
import time
import os
import openapi_client
from openapi_client.models.o_auth_token import OAuthToken
from openapi_client.models.user_profile import UserProfile
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:3000
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost:3000"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

configuration.access_token = os.environ["ACCESS_TOKEN"]

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.UsersApi(api_client)
    o_auth_token = openapi_client.OAuthToken() # OAuthToken |  (optional)

    try:
        # /users/authenticate/from_token [POST]
        api_response = api_instance.authenticate_from_oauth_token(o_auth_token=o_auth_token)
        print("The response of UsersApi->authenticate_from_oauth_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->authenticate_from_oauth_token: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **o_auth_token** | [**OAuthToken**](OAuthToken.md)|  | [optional] 

### Return type

[**UserProfile**](UserProfile.md)

### Authorization

[auth0](../README.md#auth0), [auth0](../README.md#auth0), [auth0](../README.md#auth0)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | OK |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **users_disconnect_user**
> Users users_disconnect_user(user)

/users/{user}/disconnect [POST]

Locally Removing a user for the purpose of Signing Out

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.users import Users
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
    api_instance = openapi_client.UsersApi(api_client)
    user = 'user_example' # str | 

    try:
        # /users/{user}/disconnect [POST]
        api_response = api_instance.users_disconnect_user(user)
        print("The response of UsersApi->users_disconnect_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->users_disconnect_user: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user** | **str**|  | 

### Return type

[**Users**](Users.md)

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

# **users_snapshot**
> Users users_snapshot()

/users [GET]

this will return a snapshot of all of the users that are in the users database. TODO might want to make this internal.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.users import Users
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
    api_instance = openapi_client.UsersApi(api_client)

    try:
        # /users [GET]
        api_response = api_instance.users_snapshot()
        print("The response of UsersApi->users_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->users_snapshot: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

[**Users**](Users.md)

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

# **users_specific_user_snapshot**
> UserProfile users_specific_user_snapshot(user)

/users/{user} [GET] Scoped to Users

This enables the client to get the current user.  This endpoint will return a UserPRofile or will throw an error since you are sending user uid.

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.user_profile import UserProfile
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
    api_instance = openapi_client.UsersApi(api_client)
    user = '497f6eca-6276-4993-bfeb-53cbbbba6f08' # str | The id (uuid) for a specific user.

    try:
        # /users/{user} [GET] Scoped to Users
        api_response = api_instance.users_specific_user_snapshot(user)
        print("The response of UsersApi->users_specific_user_snapshot:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling UsersApi->users_specific_user_snapshot: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **user** | **str**| The id (uuid) for a specific user. | 

### Return type

[**UserProfile**](UserProfile.md)

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

