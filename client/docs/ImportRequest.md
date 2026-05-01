# ImportRequest

Request body for rule import.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rules** | **List[Dict[str, object]]** |  | 
**mode** | **str** |  | [optional] [default to 'merge']

## Example

```python
from ds_policy_engine.models.import_request import ImportRequest

# TODO update the JSON string below
json = "{}"
# create an instance of ImportRequest from a JSON string
import_request_instance = ImportRequest.from_json(json)
# print the JSON string representation of the object
print(ImportRequest.to_json())

# convert the object into a dict
import_request_dict = import_request_instance.to_dict()
# create an instance of ImportRequest from a dict
import_request_from_dict = ImportRequest.from_dict(import_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


