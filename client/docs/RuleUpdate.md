# RuleUpdate

Schema for partially updating an existing rule.  All fields are optional; only the supplied fields are modified. Omitted fields retain their current values.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **str** |  | [optional] 
**description** | **str** |  | [optional] 
**role** | **str** |  | [optional] 
**institute** | **str** |  | [optional] 
**permissions** | **List[str]** |  | [optional] 
**enabled** | **bool** |  | [optional] 

## Example

```python
from ds_policy_engine.models.rule_update import RuleUpdate

# TODO update the JSON string below
json = "{}"
# create an instance of RuleUpdate from a JSON string
rule_update_instance = RuleUpdate.from_json(json)
# print the JSON string representation of the object
print(RuleUpdate.to_json())

# convert the object into a dict
rule_update_dict = rule_update_instance.to_dict()
# create an instance of RuleUpdate from a dict
rule_update_from_dict = RuleUpdate.from_dict(rule_update_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


