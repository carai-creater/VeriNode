"""A2A Well-Known agent-card.json のスモークテスト。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("DISABLE_DOTENV", "1")
    monkeypatch.delenv("SERPER_API_KEY", raising=False)
    monkeypatch.setenv("VERIFY_SKIP_PAYMENT", "1")

    import app.config as config_module

    config_module.get_settings.cache_clear()
    from app.main import app

    with TestClient(app) as c:
        yield c
    config_module.get_settings.cache_clear()


def test_agent_card_well_known(client: TestClient):
    r = client.get("/.well-known/agent-card.json")
    assert r.status_code == 200
    assert "application/json" in r.headers.get("content-type", "")
    assert "max-age" in r.headers.get("cache-control", "").lower()
    data = r.json()
    assert data.get("name") == "VeriNode"
    assert "supportedInterfaces" in data
    assert len(data["supportedInterfaces"]) >= 1
    assert data["supportedInterfaces"][0].get("protocolBinding") == "HTTP+JSON"
    assert "skills" in data and len(data["skills"]) >= 1
    assert data["skills"][0].get("id") == "verinode-verify"
