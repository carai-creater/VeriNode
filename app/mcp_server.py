"""
Model Context Protocol (stdio) サーバー — 公式 SDK と同様に 1 行 1 JSON の JSON-RPC。

`verify_information` ツールを公開。Python 3.9+（公式 mcp パッケージ不要）。

起動: python -m app.mcp_server
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

import httpx

from app.branding import APP_VERSION, SERVICE_NAME
from app.config import get_settings
from app.verify_service import verify_claim

PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = SERVICE_NAME
SERVER_VERSION = APP_VERSION


def _tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "name": "verify_information",
            "description": (
                f"{SERVICE_NAME}: ウェブ検索（Serper または Google Custom Search）に基づき、"
                "与えられた主張の妥当性を 0.0〜1.0 でスコアし、参照 URL と要約理由を返します。"
            ),
            "inputSchema": {
                "type": "object",
                "properties": {
                    "claim": {
                        "type": "string",
                        "description": "検証したい事実・主張（自然文）",
                    },
                },
                "required": ["claim"],
            },
        }
    ]


def _reply(msg_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "result": result}


def _error(msg_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _write_message(obj: dict[str, Any]) -> None:
    line = json.dumps(obj, ensure_ascii=False)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


async def _handle_tools_call(params: dict[str, Any]) -> dict[str, Any]:
    name = params.get("name")
    arguments = params.get("arguments") or {}
    if name != "verify_information":
        return {
            "content": [{"type": "text", "text": f"Unknown tool: {name}"}],
            "isError": True,
        }

    claim = arguments.get("claim")
    if not claim or not str(claim).strip():
        return {
            "content": [{"type": "text", "text": "claim は必須です"}],
            "isError": True,
        }

    settings = get_settings()
    if not settings.serper_api_key and (not settings.google_cse_api_key or not settings.google_cse_cx):
        return {
            "content": [
                {
                    "type": "text",
                    "text": "検索 API 未設定: SERPER_API_KEY または GOOGLE_CSE_API_KEY + GOOGLE_CSE_CX",
                }
            ],
            "isError": True,
        }

    async with httpx.AsyncClient() as client:
        try:
            result = await verify_claim(str(claim), client, settings)
        except httpx.HTTPStatusError as e:
            return {
                "content": [{"type": "text", "text": f"検索 API エラー: HTTP {e.response.status_code}"}],
                "isError": True,
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"検証エラー: {e!s}"}],
                "isError": True,
            }

    payload = json.dumps(result, ensure_ascii=False)
    return {"content": [{"type": "text", "text": payload}], "isError": False}


async def _dispatch(msg: dict[str, Any]) -> None:
    msg_id = msg.get("id")
    method = msg.get("method")
    params = msg.get("params") or {}

    # 通知には応答しない
    if msg_id is None and method and method.startswith("notifications/"):
        return

    if method == "initialize":
        client_version = params.get("protocolVersion", PROTOCOL_VERSION)
        _write_message(
            _reply(
                msg_id,
                {
                    "protocolVersion": client_version if isinstance(client_version, str) else PROTOCOL_VERSION,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                },
            )
        )
        return

    if method == "tools/list":
        _write_message(_reply(msg_id, {"tools": _tool_definitions()}))
        return

    if method == "tools/call":
        out = await _handle_tools_call(params if isinstance(params, dict) else {})
        _write_message(_reply(msg_id, out))
        return

    if method == "ping":
        _write_message(_reply(msg_id, {}))
        return

    if msg_id is not None:
        _write_message(_error(msg_id, -32601, f"Method not found: {method}"))


async def run() -> None:
    loop = asyncio.get_running_loop()
    while True:
        line: str = await loop.run_in_executor(None, sys.stdin.readline)
        if line == "":
            break
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(msg, dict):
            continue
        await _dispatch(msg)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
