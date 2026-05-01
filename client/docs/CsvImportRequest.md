# CsvImportRequest

Request body for CSV import.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**csv_content** | **str** |  | 
**mode** | **str** |  | [optional] [default to 'merge']

## Example

```python
from ds_policy_engine.models.csv_import_request import CsvImportRequest

# TODO update the JSON string below
json = "{}"
# create an instance of CsvImportRequest from a JSON string
csv_import_request_instance = CsvImportRequest.from_json(json)
# print the JSON string representation of the object
print(CsvImportRequest.to_json())

# convert the object into a dict
csv_import_request_dict = csv_import_request_instance.to_dict()
# create an instance of CsvImportRequest from a dict
csv_import_request_from_dict = CsvImportRequest.from_dict(csv_import_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


