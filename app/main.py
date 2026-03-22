from __future__ import annotations

from typing import AsyncIterator

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from starlette.middleware.cors import CORSMiddleware

from app.agent_card import build_agent_card
from app.branding import APP_VERSION, SERVICE_NAME, SERVICE_TAGLINE
from app.config import Settings, get_settings
from app.middleware.payment import PaymentRequiredMiddleware
from app.models import VerifyRequest, VerifyResponse
from app.routers import billing, webhooks
from app.verify_service import verify_claim

app = FastAPI(
    title=f"{SERVICE_NAME} — Fact-check API",
    description=SERVICE_TAGLINE,
    version=APP_VERSION,
)

app.add_middleware(PaymentRequiredMiddleware)
app.include_router(billing.router)
app.include_router(webhooks.router)


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as client:
        yield client


@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/")
async def root():
    return {
        "service": SERVICE_NAME,
        "tagline": SERVICE_TAGLINE,
        "docs": "/docs",
        "agent_card": "/.well-known/ai-agent.json",
        "verify": "POST /verify",
        "billing": "POST /billing/checkout-session",
        "mcp": "stdio: python -m app.mcp_server",
    }


@app.get("/.well-known/ai-agent.json", include_in_schema=False)
async def ai_agent_card(request: Request, settings: Settings = Depends(get_settings)):
    """他エージェント向けの能力・認証・エンドポイント記述。"""
    return build_agent_card(request, settings)


@app.post("/verify", response_model=VerifyResponse)
async def verify(
    body: VerifyRequest,
    client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
) -> VerifyResponse:
    if not settings.serper_api_key and (not settings.google_cse_api_key or not settings.google_cse_cx):
        raise HTTPException(
            status_code=503,
            detail="検索プロバイダが未設定です。SERPER_API_KEY または GOOGLE_CSE_API_KEY + GOOGLE_CSE_CX を設定してください。",
        )
    try:
        result = await verify_claim(body.claim, client, settings)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"検索 API エラー: {e.response.status_code}") from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return VerifyResponse(**result)


def _configure_cors(application: FastAPI) -> None:
    raw = get_settings().cors_allow_origins
    if not raw:
        return
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if not origins:
        return
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Payment-Link", "X-Payment-Proof"],
    )


_configure_cors(app)
