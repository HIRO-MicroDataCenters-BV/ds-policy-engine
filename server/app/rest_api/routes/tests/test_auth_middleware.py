"""Tests for the optional ds-auth integration.

These tests only verify the wiring — that auth is OFF by default, that the
permission map covers the right endpoints, and that enabling it loads the
middleware correctly. Full behavioural tests of ds-auth itself live in that
package's own test suite.

Each test reloads ``app.settings`` and ``app.main`` with monkeypatched env;
the ``_reset_main`` autouse fixture undoes the mutation after each test so
subsequent tests in the suite still see the default auth-OFF app.
"""

from __future__ import annotations

import importlib
import re

import pytest


def _reload_app():
    """Reload settings + main so env changes take effect."""
    import app.settings as settings_mod

    importlib.reload(settings_mod)
    import app.main as main_mod

    importlib.reload(main_mod)
    return main_mod


@pytest.fixture(autouse=True)
def _reset_main(monkeypatch):
    """Ensure every test starts and ends with the default (auth-off) main app.

    Without this, importlib.reload(main) during one test persists the
    middleware-wrapped app and breaks every subsequent route test in the suite.
    """
    # Clear any lingering auth env — monkeypatch undoes this at teardown too
    for var in (
        "DS__AUTH_ENABLED",
        "DS__AUTH_JWKS_URL",
        "DS__AUTH_POLICY_ENGINE_URL",
        "DS__AUTH_JWT_ISSUER",
        "DS__AUTH_JWT_AUDIENCE",
    ):
        monkeypatch.delenv(var, raising=False)
    _reload_app()
    yield
    # Restore to default state so other test files don't see auth-enabled app
    for var in (
        "DS__AUTH_ENABLED",
        "DS__AUTH_JWKS_URL",
        "DS__AUTH_POLICY_ENGINE_URL",
        "DS__AUTH_JWT_ISSUER",
        "DS__AUTH_JWT_AUDIENCE",
    ):
        monkeypatch.delenv(var, raising=False)
    _reload_app()


def test_auth_disabled_by_default():
    """With no DS__AUTH_* envs set, auth middleware is NOT installed."""
    main_mod = _reload_app()
    middleware_names = [m.cls.__name__ for m in main_mod.app.user_middleware]
    assert (
        "DataspaceAuthMiddleware" not in middleware_names
    ), f"auth middleware should be off by default; found: {middleware_names}"


def test_permission_map_covers_rule_endpoints():
    """Every rule-mutating route must have a permission mapping — ensures
    we didn't leave a rule endpoint accidentally unguarded."""
    from app.rest_api.auth_config import PERMISSION_MAP

    rule_patterns = [p for (_m, p, _perm) in PERMISSION_MAP if "rules" in p]
    # Must cover: list/create (/rules), toggle, meta
    assert any(re.search(r"\^/api/v1/rules/\?\$", p) for p in rule_patterns)
    assert any("toggle" in p for p in rule_patterns)
    assert any("meta" in p for p in rule_patterns)
    # Must cover deploy + preview too
    deploy_patterns = [p for (_m, p, _perm) in PERMISSION_MAP if "deploy" in p]
    assert len(deploy_patterns) >= 1
    preview_patterns = [p for (_m, p, _perm) in PERMISSION_MAP if "preview" in p]
    assert len(preview_patterns) >= 1


def test_public_paths_include_evaluate_and_health():
    """/evaluate and /health must stay public even when auth is on."""
    from app.rest_api.auth_config import PUBLIC_PATHS

    assert "/api/v1/policies/evaluate" in PUBLIC_PATHS
    assert "/health" in PUBLIC_PATHS
    assert "/openapi.json" in PUBLIC_PATHS


def test_auth_enabled_without_jwks_url_fails(monkeypatch):
    """Starting with DS__AUTH_ENABLED=true but no JWKS URL must fail loudly."""
    monkeypatch.setenv("DS__AUTH_ENABLED", "true")
    # Deliberately NOT setting DS__AUTH_JWKS_URL

    with pytest.raises(RuntimeError, match="DS__AUTH_JWKS_URL"):
        _reload_app()


def test_auth_enabled_installs_middleware(monkeypatch):
    """With DS__AUTH_ENABLED=true + a JWKS URL, the middleware is wired."""
    monkeypatch.setenv("DS__AUTH_ENABLED", "true")
    monkeypatch.setenv("DS__AUTH_JWKS_URL", "http://login.test/.well-known/jwks.json")
    main_mod = _reload_app()
    middleware_names = [m.cls.__name__ for m in main_mod.app.user_middleware]
    assert "DataspaceAuthMiddleware" in middleware_names
