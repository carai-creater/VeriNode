"""registration テンプレートとペイロードスクリプトの健全性。"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_a2a_registry_template_placeholders():
    raw = (ROOT / "registration" / "a2a-registry.agent_card.json").read_text(encoding="utf-8")
    assert "__PUBLIC_BASE_URL__" in raw
    filled = raw.replace("__PUBLIC_BASE_URL__", "https://example.com")
    data = json.loads(filled)
    assert data["url"] == "https://example.com"
    assert "example.com/verify" in data["skills"][0]["description"]


def test_print_a2a_registry_payload_runs():
    env = {**os.environ, "PUBLIC_BASE_URL": "https://example.com"}
    out = subprocess.check_output(
        [sys.executable, str(ROOT / "scripts" / "print_a2a_registry_payload.py")],
        cwd=str(ROOT),
        env=env,
        text=True,
    )
    body = json.loads(out)
    assert body["jsonrpc"] == "2.0"
    assert body["method"] == "register_agent"
    ac = body["params"]["agent_card"]
    assert ac["url"] == "https://example.com"
    assert ac["skills"][0]["id"] == "verinode-verify"
