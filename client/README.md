# ds_policy_engine (Python client)

Auto-generated Python SDK for the `ds-policy-engine` FastAPI service. Published to PyPI as `ds_policy_engine` on semver tag pushes (via `.github/workflows/client.yaml`).

**Do not edit files under this directory by hand** — they are regenerated from `../api/openapi.yaml` by `../tools/client_generator/generate.py` (runs as a pre-commit hook and as a CI diff-check).

## Regenerate locally

```bash
poetry --project server run python ./tools/extract_openapi.py app.main:app \
    --app-dir ./server --out ./api/openapi.yaml --app_version_file ./VERSION
poetry --project server run python ./tools/client_generator/generate.py ./api/openapi.yaml
```

## Usage (once published)

```python
from ds_policy_engine import ApiClient, Configuration
from ds_policy_engine.api.default_api import DefaultApi

config = Configuration(host="http://ds-policy-engine.ki.nextgen.hiro-develop.nl")
with ApiClient(config) as client:
    api = DefaultApi(client)
    result = api.evaluate_policy({...})
```
