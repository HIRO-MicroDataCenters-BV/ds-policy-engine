# ds_policy_engine.OPAManagementApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_opa_policy_api_v1_opa_policies_policy_id_delete**](OPAManagementApi.md#delete_opa_policy_api_v1_opa_policies_policy_id_delete) | **DELETE** /api/v1/opa/policies/{policy_id} | Delete OPA policy
[**list_opa_policies_api_v1_opa_policies_get**](OPAManagementApi.md#list_opa_policies_api_v1_opa_policies_get) | **GET** /api/v1/opa/policies | List OPA policies
[**opa_health_api_v1_opa_health_get**](OPAManagementApi.md#opa_health_api_v1_opa_health_get) | **GET** /api/v1/opa/health | OPA health


# **delete_opa_policy_api_v1_opa_policies_policy_id_delete**
> object delete_opa_policy_api_v1_opa_policies_policy_id_delete(policy_id)

Delete OPA policy

Remove a policy from OPA

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
    api_instance = ds_policy_engine.OPAManagementApi(api_client)
    policy_id = 'policy_id_example' # str | 

    try:
        # Delete OPA policy
        api_response = api_instance.delete_opa_policy_api_v1_opa_policies_policy_id_delete(policy_id)
        print("The response of OPAManagementApi->delete_opa_policy_api_v1_opa_policies_policy_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OPAManagementApi->delete_opa_policy_api_v1_opa_policies_policy_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_id** | **str**|  | 

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
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_opa_policies_api_v1_opa_policies_get**
> object list_opa_policies_api_v1_opa_policies_get()

List OPA policies

List all policies currently loaded in OPA

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
    api_instance = ds_policy_engine.OPAManagementApi(api_client)

    try:
        # List OPA policies
        api_response = api_instance.list_opa_policies_api_v1_opa_policies_get()
        print("The response of OPAManagementApi->list_opa_policies_api_v1_opa_policies_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OPAManagementApi->list_opa_policies_api_v1_opa_policies_get: %s\n" % e)
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

# **opa_health_api_v1_opa_health_get**
> object opa_health_api_v1_opa_health_get()

OPA health

Check if OPA is reachable

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
    api_instance = ds_policy_engine.OPAManagementApi(api_client)

    try:
        # OPA health
        api_response = api_instance.opa_health_api_v1_opa_health_get()
        print("The response of OPAManagementApi->opa_health_api_v1_opa_health_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OPAManagementApi->opa_health_api_v1_opa_health_get: %s\n" % e)
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

