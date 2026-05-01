# DeployRequest

Optional body for deploy — includes deployer name.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**deployed_by** | **str** |  | [optional] [default to 'system']

## Example

```python
from ds_policy_engine.models.deploy_request import DeployRequest

# TODO update the JSON string below
json = "{}"
# create an instance of DeployRequest from a JSON string
deploy_request_instance = DeployRequest.from_json(json)
# print the JSON string representation of the object
print(DeployRequest.to_json())

# convert the object into a dict
deploy_request_dict = deploy_request_instance.to_dict()
# create an instance of DeployRequest from a dict
deploy_request_from_dict = DeployRequest.from_dict(deploy_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


