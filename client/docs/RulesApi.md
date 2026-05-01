# ds_policy_engine.RulesApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_rule_api_v1_rules_post**](RulesApi.md#create_rule_api_v1_rules_post) | **POST** /api/v1/rules | Create rule
[**delete_rule_api_v1_rules_rule_id_delete**](RulesApi.md#delete_rule_api_v1_rules_rule_id_delete) | **DELETE** /api/v1/rules/{rule_id} | Delete rule
[**export_rego_api_v1_rules_export_rego_get**](RulesApi.md#export_rego_api_v1_rules_export_rego_get) | **GET** /api/v1/rules/export/rego | Export generated Rego policy
[**export_rules_api_v1_rules_export_json_get**](RulesApi.md#export_rules_api_v1_rules_export_json_get) | **GET** /api/v1/rules/export/json | Export all rules
[**export_rules_csv_api_v1_rules_export_csv_get**](RulesApi.md#export_rules_csv_api_v1_rules_export_csv_get) | **GET** /api/v1/rules/export/csv | Export rules as CSV
[**get_rule_api_v1_rules_rule_id_get**](RulesApi.md#get_rule_api_v1_rules_rule_id_get) | **GET** /api/v1/rules/{rule_id} | Get rule
[**get_rules_meta_api_v1_rules_meta_get**](RulesApi.md#get_rules_meta_api_v1_rules_meta_get) | **GET** /api/v1/rules/meta | All rule metadata
[**import_rules_api_v1_rules_import_json_post**](RulesApi.md#import_rules_api_v1_rules_import_json_post) | **POST** /api/v1/rules/import/json | Import rules from JSON
[**import_rules_csv_api_v1_rules_import_csv_post**](RulesApi.md#import_rules_csv_api_v1_rules_import_csv_post) | **POST** /api/v1/rules/import/csv | Import rules from CSV
[**list_known_permissions_api_v1_rules_meta_permissions_get**](RulesApi.md#list_known_permissions_api_v1_rules_meta_permissions_get) | **GET** /api/v1/rules/meta/permissions | List known permissions
[**list_known_roles_api_v1_rules_meta_roles_get**](RulesApi.md#list_known_roles_api_v1_rules_meta_roles_get) | **GET** /api/v1/rules/meta/roles | List known roles
[**list_rules_api_v1_rules_get**](RulesApi.md#list_rules_api_v1_rules_get) | **GET** /api/v1/rules | List rules
[**toggle_rule_api_v1_rules_rule_id_toggle_patch**](RulesApi.md#toggle_rule_api_v1_rules_rule_id_toggle_patch) | **PATCH** /api/v1/rules/{rule_id}/toggle | Toggle rule
[**update_rule_api_v1_rules_rule_id_put**](RulesApi.md#update_rule_api_v1_rules_rule_id_put) | **PUT** /api/v1/rules/{rule_id} | Update rule


# **create_rule_api_v1_rules_post**
> object create_rule_api_v1_rules_post(rule_create)

Create rule

Create a new policy rule

### Example


```python
import ds_policy_engine
from ds_policy_engine.models.rule_create import RuleCreate
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
    api_instance = ds_policy_engine.RulesApi(api_client)
    rule_create = ds_policy_engine.RuleCreate() # RuleCreate | 

    try:
        # Create rule
        api_response = api_instance.create_rule_api_v1_rules_post(rule_create)
        print("The response of RulesApi->create_rule_api_v1_rules_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->create_rule_api_v1_rules_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_create** | [**RuleCreate**](RuleCreate.md)|  | 

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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_rule_api_v1_rules_rule_id_delete**
> object delete_rule_api_v1_rules_rule_id_delete(rule_id)

Delete rule

Delete a rule by ID

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
    api_instance = ds_policy_engine.RulesApi(api_client)
    rule_id = 'rule_id_example' # str | 

    try:
        # Delete rule
        api_response = api_instance.delete_rule_api_v1_rules_rule_id_delete(rule_id)
        print("The response of RulesApi->delete_rule_api_v1_rules_rule_id_delete:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->delete_rule_api_v1_rules_rule_id_delete: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **str**|  | 

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

# **export_rego_api_v1_rules_export_rego_get**
> str export_rego_api_v1_rules_export_rego_get()

Export generated Rego policy

Export the generated Rego source code for audit, Git versioning, or compliance

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
    api_instance = ds_policy_engine.RulesApi(api_client)

    try:
        # Export generated Rego policy
        api_response = api_instance.export_rego_api_v1_rules_export_rego_get()
        print("The response of RulesApi->export_rego_api_v1_rules_export_rego_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->export_rego_api_v1_rules_export_rego_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **export_rules_api_v1_rules_export_json_get**
> object export_rules_api_v1_rules_export_json_get()

Export all rules

Export all rules as a JSON backup file

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
    api_instance = ds_policy_engine.RulesApi(api_client)

    try:
        # Export all rules
        api_response = api_instance.export_rules_api_v1_rules_export_json_get()
        print("The response of RulesApi->export_rules_api_v1_rules_export_json_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->export_rules_api_v1_rules_export_json_get: %s\n" % e)
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

# **export_rules_csv_api_v1_rules_export_csv_get**
> str export_rules_csv_api_v1_rules_export_csv_get()

Export rules as CSV

Export all rules as a CSV file for bulk editing in spreadsheets

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
    api_instance = ds_policy_engine.RulesApi(api_client)

    try:
        # Export rules as CSV
        api_response = api_instance.export_rules_csv_api_v1_rules_export_csv_get()
        print("The response of RulesApi->export_rules_csv_api_v1_rules_export_csv_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->export_rules_csv_api_v1_rules_export_csv_get: %s\n" % e)
```



### Parameters

This endpoint does not need any parameter.

### Return type

**str**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_rule_api_v1_rules_rule_id_get**
> object get_rule_api_v1_rules_rule_id_get(rule_id)

Get rule

Get a single rule by ID

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
    api_instance = ds_policy_engine.RulesApi(api_client)
    rule_id = 'rule_id_example' # str | 

    try:
        # Get rule
        api_response = api_instance.get_rule_api_v1_rules_rule_id_get(rule_id)
        print("The response of RulesApi->get_rule_api_v1_rules_rule_id_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->get_rule_api_v1_rules_rule_id_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **str**|  | 

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

# **get_rules_meta_api_v1_rules_meta_get**
> object get_rules_meta_api_v1_rules_meta_get()

All rule metadata

Returns unique roles and permissions derived from existing rules

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
    api_instance = ds_policy_engine.RulesApi(api_client)

    try:
        # All rule metadata
        api_response = api_instance.get_rules_meta_api_v1_rules_meta_get()
        print("The response of RulesApi->get_rules_meta_api_v1_rules_meta_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->get_rules_meta_api_v1_rules_meta_get: %s\n" % e)
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

# **import_rules_api_v1_rules_import_json_post**
> object import_rules_api_v1_rules_import_json_post(import_request)

Import rules from JSON

Import rules from a previously exported JSON backup

### Example


```python
import ds_policy_engine
from ds_policy_engine.models.import_request import ImportRequest
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
    api_instance = ds_policy_engine.RulesApi(api_client)
    import_request = ds_policy_engine.ImportRequest() # ImportRequest | 

    try:
        # Import rules from JSON
        api_response = api_instance.import_rules_api_v1_rules_import_json_post(import_request)
        print("The response of RulesApi->import_rules_api_v1_rules_import_json_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->import_rules_api_v1_rules_import_json_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **import_request** | [**ImportRequest**](ImportRequest.md)|  | 

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

# **import_rules_csv_api_v1_rules_import_csv_post**
> object import_rules_csv_api_v1_rules_import_csv_post(csv_import_request)

Import rules from CSV

Import rules from CSV content. Permissions should be semicolon-separated.

### Example


```python
import ds_policy_engine
from ds_policy_engine.models.csv_import_request import CsvImportRequest
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
    api_instance = ds_policy_engine.RulesApi(api_client)
    csv_import_request = ds_policy_engine.CsvImportRequest() # CsvImportRequest | 

    try:
        # Import rules from CSV
        api_response = api_instance.import_rules_csv_api_v1_rules_import_csv_post(csv_import_request)
        print("The response of RulesApi->import_rules_csv_api_v1_rules_import_csv_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->import_rules_csv_api_v1_rules_import_csv_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **csv_import_request** | [**CsvImportRequest**](CsvImportRequest.md)|  | 

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

# **list_known_permissions_api_v1_rules_meta_permissions_get**
> object list_known_permissions_api_v1_rules_meta_permissions_get()

List known permissions

Returns all unique permissions currently defined across rules

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
    api_instance = ds_policy_engine.RulesApi(api_client)

    try:
        # List known permissions
        api_response = api_instance.list_known_permissions_api_v1_rules_meta_permissions_get()
        print("The response of RulesApi->list_known_permissions_api_v1_rules_meta_permissions_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->list_known_permissions_api_v1_rules_meta_permissions_get: %s\n" % e)
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

# **list_known_roles_api_v1_rules_meta_roles_get**
> object list_known_roles_api_v1_rules_meta_roles_get()

List known roles

Returns all unique roles currently defined across rules

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
    api_instance = ds_policy_engine.RulesApi(api_client)

    try:
        # List known roles
        api_response = api_instance.list_known_roles_api_v1_rules_meta_roles_get()
        print("The response of RulesApi->list_known_roles_api_v1_rules_meta_roles_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->list_known_roles_api_v1_rules_meta_roles_get: %s\n" % e)
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

# **list_rules_api_v1_rules_get**
> object list_rules_api_v1_rules_get(page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order, role=role, enabled=enabled, search=search)

List rules

List all rules with pagination, filtering, and sorting

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
    api_instance = ds_policy_engine.RulesApi(api_client)
    page = 1 # int |  (optional) (default to 1)
    page_size = 10 # int |  (optional) (default to 10)
    sort_by = 'created_at' # str |  (optional) (default to 'created_at')
    sort_order = 'desc' # str |  (optional) (default to 'desc')
    role = 'role_example' # str |  (optional)
    enabled = True # bool |  (optional)
    search = 'search_example' # str |  (optional)

    try:
        # List rules
        api_response = api_instance.list_rules_api_v1_rules_get(page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order, role=role, enabled=enabled, search=search)
        print("The response of RulesApi->list_rules_api_v1_rules_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->list_rules_api_v1_rules_get: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page** | **int**|  | [optional] [default to 1]
 **page_size** | **int**|  | [optional] [default to 10]
 **sort_by** | **str**|  | [optional] [default to &#39;created_at&#39;]
 **sort_order** | **str**|  | [optional] [default to &#39;desc&#39;]
 **role** | **str**|  | [optional] 
 **enabled** | **bool**|  | [optional] 
 **search** | **str**|  | [optional] 

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

# **toggle_rule_api_v1_rules_rule_id_toggle_patch**
> object toggle_rule_api_v1_rules_rule_id_toggle_patch(rule_id)

Toggle rule

Enable or disable a rule

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
    api_instance = ds_policy_engine.RulesApi(api_client)
    rule_id = 'rule_id_example' # str | 

    try:
        # Toggle rule
        api_response = api_instance.toggle_rule_api_v1_rules_rule_id_toggle_patch(rule_id)
        print("The response of RulesApi->toggle_rule_api_v1_rules_rule_id_toggle_patch:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->toggle_rule_api_v1_rules_rule_id_toggle_patch: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **str**|  | 

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

# **update_rule_api_v1_rules_rule_id_put**
> object update_rule_api_v1_rules_rule_id_put(rule_id, rule_update)

Update rule

Update an existing rule

### Example


```python
import ds_policy_engine
from ds_policy_engine.models.rule_update import RuleUpdate
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
    api_instance = ds_policy_engine.RulesApi(api_client)
    rule_id = 'rule_id_example' # str | 
    rule_update = ds_policy_engine.RuleUpdate() # RuleUpdate | 

    try:
        # Update rule
        api_response = api_instance.update_rule_api_v1_rules_rule_id_put(rule_id, rule_update)
        print("The response of RulesApi->update_rule_api_v1_rules_rule_id_put:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling RulesApi->update_rule_api_v1_rules_rule_id_put: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **rule_id** | **str**|  | 
 **rule_update** | [**RuleUpdate**](RuleUpdate.md)|  | 

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

