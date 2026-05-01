# PreviewRequest

Optional body for the preview endpoint.  When ``rules`` is provided the Rego is generated from those rules instead of the saved manifest — useful for live-previewing unsaved edits in the Policy Builder.

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**rules** | **List[Dict[str, object]]** |  | [optional] 

## Example

```python
from ds_policy_engine.models.preview_request import PreviewRequest

# TODO update the JSON string below
json = "{}"
# create an instance of PreviewRequest from a JSON string
preview_request_instance = PreviewRequest.from_json(json)
# print the JSON string representation of the object
print(PreviewRequest.to_json())

# convert the object into a dict
preview_request_dict = preview_request_instance.to_dict()
# create an instance of PreviewRequest from a dict
preview_request_from_dict = PreviewRequest.from_dict(preview_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


