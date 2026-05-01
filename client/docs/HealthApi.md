# ds_policy_engine.HealthApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**health_check_health_get**](HealthApi.md#health_check_health_get) | **GET** /health | Health check


# **health_check_health_get**
> object health_check_health_get()

Health check

Service and policy engine health status

### Example


```python
import ds_policy_engine
from ds_policy_engine.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = ds_policy_engine.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with ds_policy_engine.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = ds_policy_engine.HealthApi(api_client)

    try:
        # Health check
        api_response = api_instance.health_check_health_get()
        print("The response of HealthApi->health_check_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling HealthApi->health_check_health_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

