# ds_policy_engine.PolicyEvaluationApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**deploy_history_api_v1_policies_deploy_history_get**](PolicyEvaluationApi.md#deploy_history_api_v1_policies_deploy_history_get) | **GET** /api/v1/policies/deploy-history | Deploy history
[**deploy_policies_api_v1_policies_deploy_post**](PolicyEvaluationApi.md#deploy_policies_api_v1_policies_deploy_post) | **POST** /api/v1/policies/deploy | Deploy policies to Policy Agent
[**evaluate_policy_api_v1_policies_evaluate_post**](PolicyEvaluationApi.md#evaluate_policy_api_v1_policies_evaluate_post) | **POST** /api/v1/policies/evaluate | Evaluate policy
[**policy_overview_api_v1_policies_overview_get**](PolicyEvaluationApi.md#policy_overview_api_v1_policies_overview_get) | **GET** /api/v1/policies/overview | Policy manager overview
[**preview_rego_api_v1_policies_preview_post**](PolicyEvaluationApi.md#preview_rego_api_v1_policies_preview_post) | **POST** /api/v1/policies/preview | Preview generated Rego


# **deploy_history_api_v1_policies_deploy_history_get**
> object deploy_history_api_v1_policies_deploy_history_get()

Deploy history

Returns the recent deploy history log

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
    api_instance = ds_policy_engine.PolicyEvaluationApi(api_client)

    try:
        # Deploy history
        api_response = api_instance.deploy_history_api_v1_policies_deploy_history_get()
        print("The response of PolicyEvaluationApi->deploy_history_api_v1_policies_deploy_history_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PolicyEvaluationApi->deploy_history_api_v1_policies_deploy_history_get: %s\n" % e)
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

# **deploy_policies_api_v1_policies_deploy_post**
> object deploy_policies_api_v1_policies_deploy_post(deploy_request=deploy_request)

Deploy policies to Policy Agent

Generate Rego and push to the policy agent

### Example


```python
import ds_policy_engine
from ds_policy_engine.models.deploy_request import DeployRequest
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
    api_instance = ds_policy_engine.PolicyEvaluationApi(api_client)
    deploy_request = ds_policy_engine.DeployRequest() # DeployRequest |  (optional)

    try:
        # Deploy policies to Policy Agent
        api_response = api_instance.deploy_policies_api_v1_policies_deploy_post(deploy_request=deploy_request)
        print("The response of PolicyEvaluationApi->deploy_policies_api_v1_policies_deploy_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PolicyEvaluationApi->deploy_policies_api_v1_policies_deploy_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **deploy_request** | [**DeployRequest**](DeployRequest.md)|  | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **evaluate_policy_api_v1_policies_evaluate_post**
> object evaluate_policy_api_v1_policies_evaluate_post(policy_evaluation_request)

Evaluate policy

Evaluate user permissions based on role and institute

### Example


```python
import ds_policy_engine
from ds_policy_engine.models.policy_evaluation_request import PolicyEvaluationRequest
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
    api_instance = ds_policy_engine.PolicyEvaluationApi(api_client)
    policy_evaluation_request = ds_policy_engine.PolicyEvaluationRequest() # PolicyEvaluationRequest | 

    try:
        # Evaluate policy
        api_response = api_instance.evaluate_policy_api_v1_policies_evaluate_post(policy_evaluation_request)
        print("The response of PolicyEvaluationApi->evaluate_policy_api_v1_policies_evaluate_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PolicyEvaluationApi->evaluate_policy_api_v1_policies_evaluate_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **policy_evaluation_request** | [**PolicyEvaluationRequest**](PolicyEvaluationRequest.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **policy_overview_api_v1_policies_overview_get**
> object policy_overview_api_v1_policies_overview_get()

Policy manager overview

Stats, conflicts, and deploy info for the manager dashboard

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
    api_instance = ds_policy_engine.PolicyEvaluationApi(api_client)

    try:
        # Policy manager overview
        api_response = api_instance.policy_overview_api_v1_policies_overview_get()
        print("The response of PolicyEvaluationApi->policy_overview_api_v1_policies_overview_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PolicyEvaluationApi->policy_overview_api_v1_policies_overview_get: %s\n" % e)
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

# **preview_rego_api_v1_policies_preview_post**
> object preview_rego_api_v1_policies_preview_post(preview_request=preview_request)

Preview generated Rego

Preview Rego from saved rules, or pass custom rules in the body for live preview

### Example


```python
import ds_policy_engine
from ds_policy_engine.models.preview_request import PreviewRequest
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
    api_instance = ds_policy_engine.PolicyEvaluationApi(api_client)
    preview_request = ds_policy_engine.PreviewRequest() # PreviewRequest |  (optional)

    try:
        # Preview generated Rego
        api_response = api_instance.preview_rego_api_v1_policies_preview_post(preview_request=preview_request)
        print("The response of PolicyEvaluationApi->preview_rego_api_v1_policies_preview_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PolicyEvaluationApi->preview_rego_api_v1_policies_preview_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **preview_request** | [**PreviewRequest**](PreviewRequest.md)|  | [optional] 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

