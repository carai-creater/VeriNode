#!/usr/bin/env python3
"""
A2A Registry（api.a2a-registry.dev）向け register_agent の JSON-RPC ボディを標準出力に出す（内容確認用）。

使用例:
  PUBLIC_BASE_URL=https://verinode.onrender.com python3 scripts/print_a2a_registry_payload.py

そのまま送る場合（自己責任）:
  PUBLIC_BASE_URL=https://... python3 scripts/print_a2a_registry_payload.py | \
    curl -sS -X POST https://api.a2a-registry.dev/jsonrpc \
      -H "Content-Type: application/json" -d @-
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    base = os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/")
    if not base:
        print("Error: set PUBLIC_BASE_URL=https://your-production-host", file=sys.stderr)
        sys.exit(1)
    if not base.startswith("https://"):
        print("Error: use HTTPS (e.g. https://verinode.onrender.com)", file=sys.stderr)
        sys.exit(1)

    tmpl = ROOT / "registration" / "a2a-registry.agent_card.json"
    if not tmpl.is_file():
        print(f"Error: missing {tmpl}", file=sys.stderr)
        sys.exit(1)

    filled = tmpl.read_text(encoding="utf-8").replace("__PUBLIC_BASE_URL__", base)
    agent_card = json.loads(filled)

    sys.path.insert(0, str(ROOT))
    from app.branding import APP_VERSION

    agent_card["version"] = APP_VERSION

    body = {
        "jsonrpc": "2.0",
        "method": "register_agent",
        "params": {"agent_card": agent_card},
        "id": 1,
    }
    print(json.dumps(body, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
