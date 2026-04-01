"""未払いリクエストに HTTP 402 と X-Payment-Link（Stripe Checkout または固定 URL）を返すミドルウェア。

POST /verify の課金判定はエンドポイント側で行い、HTTP 200 + JSON（reason に決済 URL）を返す。
その他の保護ルートでは従来どおり 402 を返す。
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings
from app.payment_gate import is_payment_proof_valid
from app.stripe_service import create_verify_checkout_session, resolve_checkout_return_base_url


class PaymentRequiredMiddleware(BaseHTTPMiddleware):
    """支払い証明が無い場合 402（/verify を除く）。Stripe 設定時は Checkout URL を X-Payment-Link に載せる。"""

    def __init__(self, app, exempt_paths: frozenset[str] | None = None) -> None:
        super().__init__(app)
        self.exempt_paths = exempt_paths or frozenset(
            {
                "/",
                "/en",
                "/health",
                "/docs",
                "/redoc",
                "/openapi.json",
                "/.well-known/ai-agent.json",
                "/.well-known/agent-card.json",
                "/verify",
                "/billing/checkout-session",
                "/billing/success",
                "/webhooks/stripe",
            }
        )

    async def dispatch(self, request: Request, call_next) -> Response:
        settings = get_settings()
        if settings.verify_skip_payment:
            return await call_next(request)
        path = request.url.path.rstrip("/") or "/"
        normalized = path if path.startswith("/") else f"/{path}"
        if normalized in self.exempt_paths or normalized.startswith("/static"):
            return await call_next(request)

        proof = request.headers.get("X-Payment-Proof") or request.headers.get("x-payment-proof")
        if await is_payment_proof_valid(proof, settings):
            return await call_next(request)

        public_origin = resolve_checkout_return_base_url(settings)
        if settings.stripe_secret_key:
            if not public_origin:
                return JSONResponse(
                    status_code=503,
                    content={
                        "detail": "stripe_needs_public_base_url",
                        "message": (
                            "STRIPE_SECRET_KEY はあるが Checkout の戻り先が未定です。"
                            " STRIPE_CHECKOUT_RETURN_BASE_URL（例: https://verinode.onrender.com）または"
                            " PUBLIC_BASE_URL / RENDER_EXTERNAL_URL を設定してください。"
                            " ローカルなら PUBLIC_BASE_URL=http://127.0.0.1:8000（ポートは uvicorn と一致）。"
                            " Stripe を使わず固定トークンのみにする場合は STRIPE_SECRET_KEY を空にし、"
                            " VERIFY_PAYMENT_TOKEN と PAYMENT_LINK_URL を設定してください。"
                        ),
                    },
                )
            try:
                pay_url, sid = await create_verify_checkout_session(settings)
            except Exception as e:
                return JSONResponse(
                    status_code=503,
                    content={
                        "detail": "stripe_checkout_failed",
                        "message": str(e),
                    },
                )
            return JSONResponse(
                status_code=402,
                content={
                    "detail": "payment_required",
                    "message": (
                        "決済は checkout_url（またはヘッダー X-Payment-Link）の Stripe ページで行い、"
                        "支払後に返却された Checkout Session ID（cs_...）を "
                        "X-Payment-Proof ヘッダーに付けて再試行してください。"
                    ),
                    "checkout_url": pay_url,
                    "checkout_session_id": sid,
                },
                headers={"X-Payment-Link": pay_url},
            )

        if settings.verify_payment_token:
            return JSONResponse(
                status_code=402,
                content={
                    "detail": "payment_required",
                    "message": (
                        "有効な支払い証明がありません。X-Payment-Proof に VERIFY_PAYMENT_TOKEN を付与するか、"
                        "X-Payment-Link の URL で決済してください。"
                    ),
                },
                headers={"X-Payment-Link": settings.payment_link_url},
            )

        return JSONResponse(
            status_code=503,
            content={
                "detail": "payment_not_configured",
                "message": (
                    "課金が有効ですが設定が不足しています。"
                    " Stripe を使う: STRIPE_SECRET_KEY と PUBLIC_BASE_URL（または VERCEL_URL / RENDER_EXTERNAL_URL / RAILWAY_PUBLIC_DOMAIN）。"
                    " 固定トークンのみ: VERIFY_PAYMENT_TOKEN と PAYMENT_LINK_URL。"
                    " ゲートを無効にする: VERIFY_SKIP_PAYMENT=1。"
                ),
            },
        )
