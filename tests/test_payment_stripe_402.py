"""Stripe 課金経路で 402 が返ること（実 Stripe には接続しない）。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client_stripe_gate(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISABLE_DOTENV", "1")
    monkeypatch.setenv("SERPER_API_KEY", "dummy-not-used-for-this-request")
    monkeypatch.setenv("VERIFY_SKIP_PAYMENT", "0")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_fake_key_for_unit_test")
    monkeypatch.setenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000")

    async def _fake_checkout(_settings):
        return "https://checkout.stripe.test/mock-session", "cs_test_mock_session_id"

    monkeypatch.setattr(
        "app.middleware.payment.create_verify_checkout_session",
        _fake_checkout,
    )

    import app.config as config_module

    config_module.get_settings.cache_clear()
    from app.main import app

    with TestClient(app) as c:
        yield c
    config_module.get_settings.cache_clear()


def test_landing_pages_skip_payment_gate(client_stripe_gate: TestClient):
    assert client_stripe_gate.get("/").status_code == 200
    assert client_stripe_gate.get("/en").status_code == 200


def test_verify_without_proof_returns_402_stripe_checkout(client_stripe_gate: TestClient):
    r = client_stripe_gate.post("/verify", json={"claim": "anything"})
    assert r.status_code == 402
    assert r.headers.get("X-Payment-Link") == "https://checkout.stripe.test/mock-session"
    body = r.json()
    assert body.get("detail") == "payment_required"
    assert body.get("checkout_session_id") == "cs_test_mock_session_id"
