"""エージェント発見用メタデータ。

- `build_agent_card`: 従来の `/.well-known/ai-agent.json`（VeriNode 独自拡張あり）
- `build_a2a_agent_card`: [Google A2A](https://github.com/google/A2A) の Well-Known `/.well-known/agent-card.json` 向け（camelCase）
"""

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
                "POST /verify は未払い時も HTTP 200 を返し、JSON の status が payment_required のときは checkout_url に Stripe が発行した決済ページ URL（session.url）、"
                "reason にも同じ URL を含む案内、ヘッダー X-Payment-Link にも同じ URL がある場合があります。"
                "決済リンクは ID から組み立てず checkout_url を開く。決済後は Checkout Session ID（cs_...）をヘッダー X-Payment-Proof またはクエリ payment_proof に付けて POST /verify を再試行する。"
                " 開発用に VERIFY_PAYMENT_TOKEN をサーバが受け付ける場合は、その値を X-Payment-Proof または payment_proof に付与してもよい。"
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
            "details": "HTTP 200 で payment_required 時は checkout_url（Stripe の session.url）で決済。reason / X-Payment-Link も同じ URL。支払済み cs_... は X-Payment-Proof または ?payment_proof= で提示。",
        },
        "extensions": {
            "verinode": {
                "mcp_stdio": "python -m app.mcp_server",
                "tool_name": "verify_information",
            },
        },
    }


def build_a2a_agent_card(request: Request, settings: Settings) -> Dict[str, Any]:
    """
    Google A2A 仕様の Agent Card 例に沿った公開用 JSON（JSON フィールドは camelCase）。

    注: 本サービスは A2A コアの SendMessage / Task API は実装していません。
    HTTP+JSON の `POST /verify` と課金（未払い時は 200 + payment_required）を skills と metadata で明示します。
    """
    base = _public_origin(request, settings)
    verify_desc = (
        f"REST API: POST {base}/verify with JSON body {{\"claim\": \"<text>\"}}. "
        "Returns verification score, sources, and reason. "
        "If payment is required, responds with HTTP 200, status payment_required, field checkout_url is the Stripe-hosted payment URL (session.url), "
        "reason includes the same URL, and header X-Payment-Link matches; "
        "after payment, retry with query payment_proof=cs_... or header X-Payment-Proof set to the Checkout Session id. "
        "Does not implement A2A SendMessage; use this REST contract."
    )
    return {
        "name": SERVICE_NAME,
        "description": SERVICE_TAGLINE,
        "version": APP_VERSION,
        "supportedInterfaces": [
            {
                "url": base,
                "protocolBinding": "HTTP+JSON",
                "protocolVersion": "0.3",
            }
        ],
        "capabilities": {
            "streaming": False,
            "pushNotifications": False,
        },
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "documentationUrl": f"{base}/docs",
        "skills": [
            {
                "id": "verinode-verify",
                "name": "Fact-check claim",
                "description": verify_desc,
                "tags": ["fact-check", "verification", "search", "rest", "stripe"],
                "examples": ['POST /verify  {"claim": "検証したい主張"}'],
                "inputModes": ["application/json"],
                "outputModes": ["application/json"],
            }
        ],
        "metadata": {
            "legacyAgentDescriptor": f"{base}/.well-known/ai-agent.json",
            "openapiUrl": f"{base}/openapi.json",
            "pricingJpyTaxIncludedPerRequest": 100,
            "note": "Not a full A2A message/task server; discovery uses A2A Agent Card shape.",
        },
    }
