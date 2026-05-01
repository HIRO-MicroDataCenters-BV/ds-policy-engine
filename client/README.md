# Python client
API version: 0.1.0

## Requirements

- Python 3.10+
- Docker engine. [Documentation](https://docs.docker.com/engine/install/)

## Installation & Usage

1. If you don't have `Poetry` installed run:

```bash
pip install poetry
```

2. Install dependencies:

```bash
poetry config virtualenvs.in-project true
poetry install --no-root
```

3. Running tests:

```bash
poetry run pytest
```

You can test the application for multiple versions of Python. To do this, you need to install the required Python versions on your operating system, specify these versions in the tox.ini file, and then run the tests:
```bash
poetry run tox
```
Add the tox.ini file to `client/.openapi-generator-ignore` so that it doesn't get overwritten during client generation.

4. Building package:

```bash
poetry build
```

5. Publishing
```bash
poetry config pypi-token.pypi <pypi token>
poetry publish
```

## Client generator
To generate the client, execute the following script from the project root folder
```bash
poetry --directory server run python ./tools/client_generator/generate.py ./api/openapi.yaml
```

### Command
```bash
generate.py <file> [--asyncio]
```

#### Arguments
**file**
Specifies the input OpenAPI specification file path or URL. This argument is required for generating the Python client. The input file can be either a local file path or a URL pointing to the OpenAPI schema.

**--asyncio**
Flag to indicate whether to generate asynchronous code. If this flag is provided, the generated Python client will include asynchronous features. By default, synchronous code is generated.

#### Configuration
You can change the name of the client package in the file `/tools/client_generator/config.json`.

Add file's paths to `client/.openapi-generator-ignore` so that it doesn't get overwritten during client generation.

#### Examples

```bash
python generate.py https://<domain>/openapi.json
python generate.py https://<domain>/openapi.json --asyncio
python generate.py /<path>/openapi.yaml
python generate.py /<path>/openapi.yaml --asyncio
```

## Getting Started

Please follow the [installation procedure](#installation--usage) and then run the following:

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
    except ApiException as e:
        print("Exception when calling DatabaseApi->browse_deploy_history_api_v1_db_tables_deploy_history_get: %s\n" % e)

```

## Documentation for API Endpoints

All URIs are relative to *http://localhost*

Class | Method | HTTP request | Description
------------ | ------------- | ------------- | -------------
*DatabaseApi* | [**browse_deploy_history_api_v1_db_tables_deploy_history_get**](docs/DatabaseApi.md#browse_deploy_history_api_v1_db_tables_deploy_history_get) | **GET** /api/v1/db/tables/deploy_history | Browse deploy history table
*DatabaseApi* | [**browse_metadata_api_v1_db_tables_metadata_get**](docs/DatabaseApi.md#browse_metadata_api_v1_db_tables_metadata_get) | **GET** /api/v1/db/tables/metadata | Browse metadata table
*DatabaseApi* | [**browse_rules_api_v1_db_tables_rules_get**](docs/DatabaseApi.md#browse_rules_api_v1_db_tables_rules_get) | **GET** /api/v1/db/tables/rules | Browse rules table
*DatabaseApi* | [**db_stats_api_v1_db_stats_get**](docs/DatabaseApi.md#db_stats_api_v1_db_stats_get) | **GET** /api/v1/db/stats | Database statistics
*DatabaseApi* | [**run_query_api_v1_db_query_post**](docs/DatabaseApi.md#run_query_api_v1_db_query_post) | **POST** /api/v1/db/query | Run read-only SQL query
*DecisionMatrixApi* | [**get_decision_matrix_api_v1_decision_matrix_get**](docs/DecisionMatrixApi.md#get_decision_matrix_api_v1_decision_matrix_get) | **GET** /api/v1/decision-matrix | Get decision matrix
*HealthApi* | [**health_check_health_get**](docs/HealthApi.md#health_check_health_get) | **GET** /health | Health check
*OPAManagementApi* | [**delete_opa_policy_api_v1_opa_policies_policy_id_delete**](docs/OPAManagementApi.md#delete_opa_policy_api_v1_opa_policies_policy_id_delete) | **DELETE** /api/v1/opa/policies/{policy_id} | Delete OPA policy
*OPAManagementApi* | [**list_opa_policies_api_v1_opa_policies_get**](docs/OPAManagementApi.md#list_opa_policies_api_v1_opa_policies_get) | **GET** /api/v1/opa/policies | List OPA policies
*OPAManagementApi* | [**opa_health_api_v1_opa_health_get**](docs/OPAManagementApi.md#opa_health_api_v1_opa_health_get) | **GET** /api/v1/opa/health | OPA health
*PolicyEvaluationApi* | [**deploy_history_api_v1_policies_deploy_history_get**](docs/PolicyEvaluationApi.md#deploy_history_api_v1_policies_deploy_history_get) | **GET** /api/v1/policies/deploy-history | Deploy history
*PolicyEvaluationApi* | [**deploy_policies_api_v1_policies_deploy_post**](docs/PolicyEvaluationApi.md#deploy_policies_api_v1_policies_deploy_post) | **POST** /api/v1/policies/deploy | Deploy policies to Policy Agent
*PolicyEvaluationApi* | [**evaluate_policy_api_v1_policies_evaluate_post**](docs/PolicyEvaluationApi.md#evaluate_policy_api_v1_policies_evaluate_post) | **POST** /api/v1/policies/evaluate | Evaluate policy
*PolicyEvaluationApi* | [**policy_overview_api_v1_policies_overview_get**](docs/PolicyEvaluationApi.md#policy_overview_api_v1_policies_overview_get) | **GET** /api/v1/policies/overview | Policy manager overview
*PolicyEvaluationApi* | [**preview_rego_api_v1_policies_preview_post**](docs/PolicyEvaluationApi.md#preview_rego_api_v1_policies_preview_post) | **POST** /api/v1/policies/preview | Preview generated Rego
*RulesApi* | [**create_rule_api_v1_rules_post**](docs/RulesApi.md#create_rule_api_v1_rules_post) | **POST** /api/v1/rules | Create rule
*RulesApi* | [**delete_rule_api_v1_rules_rule_id_delete**](docs/RulesApi.md#delete_rule_api_v1_rules_rule_id_delete) | **DELETE** /api/v1/rules/{rule_id} | Delete rule
*RulesApi* | [**export_rego_api_v1_rules_export_rego_get**](docs/RulesApi.md#export_rego_api_v1_rules_export_rego_get) | **GET** /api/v1/rules/export/rego | Export generated Rego policy
*RulesApi* | [**export_rules_api_v1_rules_export_json_get**](docs/RulesApi.md#export_rules_api_v1_rules_export_json_get) | **GET** /api/v1/rules/export/json | Export all rules
*RulesApi* | [**export_rules_csv_api_v1_rules_export_csv_get**](docs/RulesApi.md#export_rules_csv_api_v1_rules_export_csv_get) | **GET** /api/v1/rules/export/csv | Export rules as CSV
*RulesApi* | [**get_rule_api_v1_rules_rule_id_get**](docs/RulesApi.md#get_rule_api_v1_rules_rule_id_get) | **GET** /api/v1/rules/{rule_id} | Get rule
*RulesApi* | [**get_rules_meta_api_v1_rules_meta_get**](docs/RulesApi.md#get_rules_meta_api_v1_rules_meta_get) | **GET** /api/v1/rules/meta | All rule metadata
*RulesApi* | [**import_rules_api_v1_rules_import_json_post**](docs/RulesApi.md#import_rules_api_v1_rules_import_json_post) | **POST** /api/v1/rules/import/json | Import rules from JSON
*RulesApi* | [**import_rules_csv_api_v1_rules_import_csv_post**](docs/RulesApi.md#import_rules_csv_api_v1_rules_import_csv_post) | **POST** /api/v1/rules/import/csv | Import rules from CSV
*RulesApi* | [**list_known_permissions_api_v1_rules_meta_permissions_get**](docs/RulesApi.md#list_known_permissions_api_v1_rules_meta_permissions_get) | **GET** /api/v1/rules/meta/permissions | List known permissions
*RulesApi* | [**list_known_roles_api_v1_rules_meta_roles_get**](docs/RulesApi.md#list_known_roles_api_v1_rules_meta_roles_get) | **GET** /api/v1/rules/meta/roles | List known roles
*RulesApi* | [**list_rules_api_v1_rules_get**](docs/RulesApi.md#list_rules_api_v1_rules_get) | **GET** /api/v1/rules | List rules
*RulesApi* | [**toggle_rule_api_v1_rules_rule_id_toggle_patch**](docs/RulesApi.md#toggle_rule_api_v1_rules_rule_id_toggle_patch) | **PATCH** /api/v1/rules/{rule_id}/toggle | Toggle rule
*RulesApi* | [**update_rule_api_v1_rules_rule_id_put**](docs/RulesApi.md#update_rule_api_v1_rules_rule_id_put) | **PUT** /api/v1/rules/{rule_id} | Update rule


## Documentation For Models

 - [CsvImportRequest](docs/CsvImportRequest.md)
 - [DeployRequest](docs/DeployRequest.md)
 - [HTTPValidationError](docs/HTTPValidationError.md)
 - [ImportRequest](docs/ImportRequest.md)
 - [PolicyEvaluationRequest](docs/PolicyEvaluationRequest.md)
 - [PreviewRequest](docs/PreviewRequest.md)
 - [QueryRequest](docs/QueryRequest.md)
 - [RuleCreate](docs/RuleCreate.md)
 - [RuleUpdate](docs/RuleUpdate.md)
 - [ValidationError](docs/ValidationError.md)
 - [ValidationErrorLocInner](docs/ValidationErrorLocInner.md)


<a id="documentation-for-authorization"></a>
## Documentation For Authorization

Endpoints do not require authorization.


## Author

all-hiro@hiro-microdatacenters.nl


