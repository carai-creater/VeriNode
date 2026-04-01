from __future__ import annotations

from typing import AsyncIterator, Optional

import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.agent_card import build_a2a_agent_card, build_agent_card
from app.branding import APP_VERSION, SERVICE_NAME, SERVICE_TAGLINE
from app.landing_pages import html_landing_en, html_landing_ja
from app.config import Settings, get_settings
from app.middleware.payment import PaymentRequiredMiddleware
from app.models import VerifyRequest, VerifyResponse
from app.payment_gate import is_payment_proof_valid
from app.routers import billing, webhooks
from app.verify_service import verify_claim
from app.stripe_service import create_verify_checkout_session, resolve_checkout_return_base_url

PAYMENT_REASON_FMT = (
    "情報の検証には100円が必要です。こちらのリンクから決済を完了してください：{url}"
)


async def _verify_response_payment_required(response: Response, settings: Settings) -> VerifyResponse:
    """未払い時: HTTP 200・VerifyResponse（reason に決済 URL、必要なら X-Payment-Link ヘッダー）。"""
    if settings.stripe_secret_key:
        public_origin = resolve_checkout_return_base_url(settings)
        if not public_origin:
            raise HTTPException(
                status_code=503,
                detail={
                    "detail": "stripe_needs_public_base_url",
                    "message": (
                        "STRIPE_SECRET_KEY はあるが Checkout の戻り先が未定です。"
                        " 本番は STRIPE_CHECKOUT_RETURN_BASE_URL=https://verinode.onrender.com のように設定するか、"
                        " PUBLIC_BASE_URL または RENDER_EXTERNAL_URL 等を設定してください。"
                        " ローカルなら PUBLIC_BASE_URL=http://127.0.0.1:8000（ポートは uvicorn と一致）。"
                        " Stripe を使わず固定トークンのみにする場合は STRIPE_SECRET_KEY を空にし、"
                        " VERIFY_PAYMENT_TOKEN と PAYMENT_LINK_URL を設定してください。"
                    ),
                },
            )
        try:
            pay_url, sid = await create_verify_checkout_session(settings)
        except Exception as e:
            raise HTTPException(
                status_code=503,
                detail={"detail": "stripe_checkout_failed", "message": str(e)},
            ) from e
        print(f"[verify] payment_required Stripe checkout_url={pay_url}", flush=True)
        response.headers["X-Payment-Link"] = pay_url
        return VerifyResponse(
            status="payment_required",
            score=0.0,
            sources=[],
            reason=PAYMENT_REASON_FMT.format(url=pay_url),
            checkout_url=pay_url,
            checkout_session_id=sid,
        )

    if settings.verify_payment_token and settings.payment_link_url:
        pay_url = settings.payment_link_url
        print(f"[verify] payment_required payment_link_url={pay_url}", flush=True)
        response.headers["X-Payment-Link"] = pay_url
        return VerifyResponse(
            status="payment_required",
            score=0.0,
            sources=[],
            reason=PAYMENT_REASON_FMT.format(url=pay_url),
            checkout_url=pay_url,
            checkout_session_id=None,
        )

    raise HTTPException(
        status_code=503,
        detail={
            "detail": "payment_not_configured",
            "message": (
                "課金が有効ですが設定が不足しています。"
                " Stripe を使う: STRIPE_SECRET_KEY と PUBLIC_BASE_URL（または VERCEL_URL / RENDER_EXTERNAL_URL / RAILWAY_PUBLIC_DOMAIN）。"
                " 固定トークンのみ: VERIFY_PAYMENT_TOKEN と PAYMENT_LINK_URL。"
                " ゲートを無効にする: VERIFY_SKIP_PAYMENT=1。"
            ),
        },
    )


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


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return HTMLResponse(content=html_landing_ja())


@app.get("/en", response_class=HTMLResponse, include_in_schema=False)
async def root_en():
    return HTMLResponse(content=html_landing_en())


@app.get("/.well-known/ai-agent.json", include_in_schema=False)
async def ai_agent_card(request: Request, settings: Settings = Depends(get_settings)):
    """他エージェント向けの能力・認証・エンドポイント記述。"""
    return build_agent_card(request, settings)


@app.get("/.well-known/agent-card.json", include_in_schema=False)
async def a2a_well_known_agent_card(request: Request, settings: Settings = Depends(get_settings)):
    """[Google A2A](https://github.com/google/A2A) の Well-Known Agent Card（discovery 用）。"""
    data = build_a2a_agent_card(request, settings)
    return JSONResponse(
        content=data,
        headers={
            "Cache-Control": "public, max-age=300",
        },
    )


@app.post("/verify", response_model=VerifyResponse)
async def verify(
    request: Request,
    response: Response,
    body: VerifyRequest,
    client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
    payment_proof: Optional[str] = Query(
        None,
        description="支払い証明（ChatGPT 等はヘッダーが使えない場合、Checkout Session ID cs_... または VERIFY_PAYMENT_TOKEN をクエリで指定）",
    ),
) -> VerifyResponse:
    if not settings.verify_skip_payment:
        header_proof = request.headers.get("X-Payment-Proof") or request.headers.get("x-payment-proof")
        hp = str(header_proof).strip() if header_proof else ""
        qp = str(payment_proof).strip() if payment_proof is not None else ""
        proof = (qp or hp) or None
        if proof:
            print(f"Payment proof received: {proof}", flush=True)
        if not await is_payment_proof_valid(proof, settings):
            return await _verify_response_payment_required(response, settings)

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
