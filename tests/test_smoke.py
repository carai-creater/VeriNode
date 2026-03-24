"""API のスモークテスト（外部 API・Stripe は呼ばない）。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISABLE_DOTENV", "1")
    monkeypatch.delenv("SERPER_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CSE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CSE_CX", raising=False)
    monkeypatch.setenv("VERIFY_SKIP_PAYMENT", "1")
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)

    import app.config as config_module

    config_module.get_settings.cache_clear()
    from app.main import app

    with TestClient(app) as c:
        yield c
    config_module.get_settings.cache_clear()


def test_health(client: TestClient):
    assert client.get("/health").json() == {"ok": True}


def test_root_japanese(client: TestClient):
    r = client.get("/")
    assert r.status_code == 200
    assert 'lang="ja"' in r.text
    assert "特定商取引法" in r.text


def test_root_english(client: TestClient):
    r = client.get("/en")
    assert r.status_code == 200
    assert 'lang="en"' in r.text
    assert "Specified Commercial Transactions" in r.text


def test_agent_card(client: TestClient):
    r = client.get("/.well-known/ai-agent.json")
    assert r.status_code == 200
    data = r.json()
    assert data.get("name") == "VeriNode"
    assert "api" in data


def test_verify_without_search_keys_returns_503(client: TestClient):
    r = client.post("/verify", json={"claim": "地球は平らである"})
    assert r.status_code == 503


def test_payment_gate_402_with_token(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISABLE_DOTENV", "1")
    monkeypatch.delenv("SERPER_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CSE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CSE_CX", raising=False)
    monkeypatch.setenv("VERIFY_SKIP_PAYMENT", "0")
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    monkeypatch.setenv("VERIFY_PAYMENT_TOKEN", "test-token-xyz")
    monkeypatch.setenv("PAYMENT_LINK_URL", "https://pay.example/checkout")

    import app.config as config_module

    config_module.get_settings.cache_clear()
    from app.main import app

    try:
        with TestClient(app) as c:
            r = c.post("/verify", json={"claim": "test"})
            assert r.status_code == 402
            assert r.headers.get("X-Payment-Link") == "https://pay.example/checkout"
            proof = c.post(
                "/verify",
                json={"claim": "test"},
                headers={"X-Payment-Proof": "test-token-xyz"},
            )
            assert proof.status_code == 503
    finally:
        config_module.get_settings.cache_clear()
