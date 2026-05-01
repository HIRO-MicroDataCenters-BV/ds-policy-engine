# ds_policy_engine.DatabaseApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**browse_deploy_history_api_v1_db_tables_deploy_history_get**](DatabaseApi.md#browse_deploy_history_api_v1_db_tables_deploy_history_get) | **GET** /api/v1/db/tables/deploy_history | Browse deploy history table
[**browse_metadata_api_v1_db_tables_metadata_get**](DatabaseApi.md#browse_metadata_api_v1_db_tables_metadata_get) | **GET** /api/v1/db/tables/metadata | Browse metadata table
[**browse_rules_api_v1_db_tables_rules_get**](DatabaseApi.md#browse_rules_api_v1_db_tables_rules_get) | **GET** /api/v1/db/tables/rules | Browse rules table
[**db_stats_api_v1_db_stats_get**](DatabaseApi.md#db_stats_api_v1_db_stats_get) | **GET** /api/v1/db/stats | Database statistics
[**run_query_api_v1_db_query_post**](DatabaseApi.md#run_query_api_v1_db_query_post) | **POST** /api/v1/db/query | Run read-only SQL query


# **browse_deploy_history_api_v1_db_tables_deploy_history_get**
> object browse_deploy_history_api_v1_db_tables_deploy_history_get()

Browse deploy history table

Return all rows from the deploy_history table.

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
    api_instance = ds_policy_engine.DatabaseApi(api_client)

    try:
        # Browse deploy history table
        api_response = api_instance.browse_deploy_history_api_v1_db_tables_deploy_history_get()
        print("The response of DatabaseApi->browse_deploy_history_api_v1_db_tables_deploy_history_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatabaseApi->browse_deploy_history_api_v1_db_tables_deploy_history_get: %s\n" % e)
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

# **browse_metadata_api_v1_db_tables_metadata_get**
> object browse_metadata_api_v1_db_tables_metadata_get()

Browse metadata table

Return all key-value pairs from the app_metadata table.

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
    api_instance = ds_policy_engine.DatabaseApi(api_client)

    try:
        # Browse metadata table
        api_response = api_instance.browse_metadata_api_v1_db_tables_metadata_get()
        print("The response of DatabaseApi->browse_metadata_api_v1_db_tables_metadata_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatabaseApi->browse_metadata_api_v1_db_tables_metadata_get: %s\n" % e)
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

# **browse_rules_api_v1_db_tables_rules_get**
> object browse_rules_api_v1_db_tables_rules_get()

Browse rules table

Return all rows from the rules table with full column data.

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
    api_instance = ds_policy_engine.DatabaseApi(api_client)

    try:
        # Browse rules table
        api_response = api_instance.browse_rules_api_v1_db_tables_rules_get()
        print("The response of DatabaseApi->browse_rules_api_v1_db_tables_rules_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatabaseApi->browse_rules_api_v1_db_tables_rules_get: %s\n" % e)
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

# **db_stats_api_v1_db_stats_get**
> object db_stats_api_v1_db_stats_get()

Database statistics

Return high-level stats: table counts, DB engine info.

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
    api_instance = ds_policy_engine.DatabaseApi(api_client)

    try:
        # Database statistics
        api_response = api_instance.db_stats_api_v1_db_stats_get()
        print("The response of DatabaseApi->db_stats_api_v1_db_stats_get:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatabaseApi->db_stats_api_v1_db_stats_get: %s\n" % e)
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

# **run_query_api_v1_db_query_post**
> object run_query_api_v1_db_query_post(query_request)

Run read-only SQL query

Execute a read-only SELECT query against the database. Only SELECT statements are allowed; DML/DDL is rejected.

### Example


```python
import ds_policy_engine
from ds_policy_engine.models.query_request import QueryRequest
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
    api_instance = ds_policy_engine.DatabaseApi(api_client)
    query_request = ds_policy_engine.QueryRequest() # QueryRequest | 

    try:
        # Run read-only SQL query
        api_response = api_instance.run_query_api_v1_db_query_post(query_request)
        print("The response of DatabaseApi->run_query_api_v1_db_query_post:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DatabaseApi->run_query_api_v1_db_query_post: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **query_request** | [**QueryRequest**](QueryRequest.md)|  | 

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

