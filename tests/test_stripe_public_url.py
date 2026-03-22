"""STRIPE_SECRET_KEY のみで PUBLIC_BASE_URL が無いとき 503（誤って example.com に誘導しない）。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_stripe_key_without_public_base_url_returns_503(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISABLE_DOTENV", "1")
    monkeypatch.setenv("SERPER_API_KEY", "dummy")
    monkeypatch.setenv("VERIFY_SKIP_PAYMENT", "0")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_fake")
    monkeypatch.delenv("PUBLIC_BASE_URL", raising=False)
    monkeypatch.delenv("VERCEL_URL", raising=False)
    monkeypatch.delenv("RENDER_EXTERNAL_URL", raising=False)
    monkeypatch.delenv("RAILWAY_PUBLIC_DOMAIN", raising=False)
    monkeypatch.delenv("VERIFY_PAYMENT_TOKEN", raising=False)

    import app.config as config_module

    config_module.get_settings.cache_clear()
    from app.main import app

    try:
        with TestClient(app) as c:
            r = c.post("/verify", json={"claim": "x"})
            assert r.status_code == 503
            assert r.json().get("detail") == "stripe_needs_public_base_url"
    finally:
        config_module.get_settings.cache_clear()
