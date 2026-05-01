# RuleCreate

Schema for creating a new authorization rule.  Defines the required and optional fields accepted when a client submits a request to create a rule. Each rule maps a role to a set of permissions.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** | Rule display name | 
**description** | **str** |  | [optional] [default to '']
**role** | **str** | Target role for this rule | 
**institute** | **str** | Institute this rule applies to | [optional] [default to '']
**permissions** | **List[str]** | Permissions granted by this rule. May be empty (the service surfaces such rules as a warning in the overview). | [optional] 
**enabled** | **bool** |  | [optional] [default to True]

## Example

```python
from ds_policy_engine.models.rule_create import RuleCreate

# TODO update the JSON string below
json = "{}"
# create an instance of RuleCreate from a JSON string
rule_create_instance = RuleCreate.from_json(json)
# print the JSON string representation of the object
print(RuleCreate.to_json())

# convert the object into a dict
rule_create_dict = rule_create_instance.to_dict()
# create an instance of RuleCreate from a dict
rule_create_from_dict = RuleCreate.from_dict(rule_create_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


