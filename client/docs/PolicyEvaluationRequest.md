# PolicyEvaluationRequest

Request body for evaluating a user's permissions against the deployed policy.  The fields identify the user whose permissions should be resolved by the policy engine. The ``role`` field is the primary input used by the Rego policy to determine the granted permission set.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | User&#39;s full name | 
**email** | **str** | User&#39;s email address | 
**role** | **str** | User&#39;s role (catalog_owner, catalog_creator, catalog_consumer) | 
**institute** | **str** | User&#39;s institute identifier | 

## Example

```python
from ds_policy_engine.models.policy_evaluation_request import PolicyEvaluationRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PolicyEvaluationRequest from a JSON string
policy_evaluation_request_instance = PolicyEvaluationRequest.from_json(json)
# print the JSON string representation of the object
print(PolicyEvaluationRequest.to_json())

# convert the object into a dict
policy_evaluation_request_dict = policy_evaluation_request_instance.to_dict()
# create an instance of PolicyEvaluationRequest from a dict
policy_evaluation_request_from_dict = PolicyEvaluationRequest.from_dict(policy_evaluation_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


