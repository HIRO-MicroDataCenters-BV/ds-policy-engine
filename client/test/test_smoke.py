"""Smoke test — keeps pytest happy when the auto-generated per-model test
stubs are disabled (we pass --global-property apiTests=false,modelTests=false
to openapi-generator so the SDK stays minimal).

Without at least one test file, ``pytest`` exits with code 5 ("no tests
collected"), which fails the client.yaml CI step.

This file is listed in ``client/.openapi-generator-ignore`` so the
generator never touches it.
"""

import importlib


def test_package_imports():
    """The package can be imported and exposes expected top-level names."""
    mod = importlib.import_module("ds_policy_engine")
    assert hasattr(mod, "ApiClient"), "expected ApiClient on the package"
    assert hasattr(mod, "Configuration"), "expected Configuration on the package"
