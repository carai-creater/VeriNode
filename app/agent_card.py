"""エージェント発見用 Agent Card（A2A 系の一般的な形に準拠）。"""

from __future__ import annotations

from typing import Any, Dict

from fastapi import Request

from app.branding import APP_VERSION, SERVICE_NAME, SERVICE_TAGLINE
from app.config import Settings
from app.stripe_service import resolve_public_base_url


def _public_origin(request: Request, settings: Settings) -> str:
    resolved = resolve_public_base_url(settings)
    if resolved:
        return resolved.rstrip("/")
    host = request.headers.get("x-forwarded-host") or request.headers.get("host")
    proto = (request.headers.get("x-forwarded-proto") or request.url.scheme or "https").split(",")[0].strip()
    if host:
        return f"{proto}://{host}".rstrip("/")
    return str(request.base_url).rstrip("/")


def build_agent_card(request: Request, settings: Settings) -> Dict[str, Any]:
    base = _public_origin(request, settings)
    return {
        "name": SERVICE_NAME,
        "description": SERVICE_TAGLINE,
        "version": APP_VERSION,
        "api": {
            "type": "a2a",
            "url": base,
            "version": "0.1",
            "endpoints": {
                "open_api": f"{base}/openapi.json",
                "verify": {"method": "POST", "path": "/verify", "content_type": "application/json"},
                "billing_checkout": {"method": "POST", "path": "/billing/checkout-session"},
            },
        },
        "auth": {
            "type": "custom",
            "instructions": (
                "保護された API では HTTP 402 の場合、レスポンスヘッダー X-Payment-Link の Stripe Checkout で支払い、"
                "完了後に返却された Checkout Session ID（cs_...）をヘッダー X-Payment-Proof に付与して再試行する。"
                " 開発用に VERIFY_PAYMENT_TOKEN をサーバが受け付ける場合は、その値を X-Payment-Proof に付与してもよい。"
            ),
        },
        "capabilities": [
            {
                "type": "verinode.verify",
                "description": "ウェブ検索に基づく主張の検証（スコア・ソース・要約）",
                "parameters": {"claim": "string", "response_schema": "VerifyResponse"},
            },
            {
                "type": "verinode.billing",
                "description": "Stripe Checkout による都度課金（円）",
                "parameters": {"currency": "jpy", "model": "payment"},
            },
        ],
        "pricing": {
            "model": "pay_per_request",
            "details": "HTTP 402 + Stripe Checkout。支払済みセッション ID を X-Payment-Proof で提示。",
        },
        "extensions": {
            "verinode": {
                "mcp_stdio": "python -m app.mcp_server",
                "tool_name": "verify_information",
            },
        },
    }
