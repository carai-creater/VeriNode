"""Stripe Checkout — 1 回払い（円）とセッション検証。"""

from __future__ import annotations

import os
from typing import Any, Optional, Tuple

import anyio
import stripe

from app.branding import SERVICE_NAME
from app.config import Settings


def resolve_public_base_url(settings: Settings) -> Optional[str]:
    if settings.public_base_url:
        return settings.public_base_url.rstrip("/")
    vercel = os.getenv("VERCEL_URL", "").strip()
    if vercel:
        if vercel.startswith("http://") or vercel.startswith("https://"):
            return vercel.rstrip("/")
        return f"https://{vercel}".rstrip("/")
    render = os.getenv("RENDER_EXTERNAL_URL", "").strip()
    if render:
        if render.startswith("http://") or render.startswith("https://"):
            return render.rstrip("/")
        return f"https://{render}".rstrip("/")
    railway = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
    if railway:
        if railway.startswith("http://") or railway.startswith("https://"):
            return railway.rstrip("/")
        return f"https://{railway}".rstrip("/")
    return None


def _create_checkout_session_sync(settings: Settings, base_url: str) -> Tuple[str, str]:
    stripe.api_key = settings.stripe_secret_key
    success = f"{base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel = f"{base_url}/?payment=canceled"

    if settings.stripe_price_id:
        line_items: list[dict[str, Any]] = [{"price": settings.stripe_price_id, "quantity": 1}]
    else:
        line_items = [
            {
                "price_data": {
                    "currency": "jpy",
                    "product_data": {
                        "name": f"{SERVICE_NAME} — verification credit",
                        "description": "Single fact-check / verify API call credit (pay-per-use).",
                    },
                    "unit_amount": int(settings.stripe_verify_unit_amount_jpy),
                },
                "quantity": 1,
            }
        ]

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=success,
        cancel_url=cancel,
        metadata={"product": "verinode_verify", "service": SERVICE_NAME},
    )
    url = session.url or ""
    sid = session.id
    if not url:
        raise RuntimeError("Stripe Checkout Session に url がありません")
    return url, sid


async def create_verify_checkout_session(settings: Settings) -> Tuple[str, str]:
    base = resolve_public_base_url(settings)
    if not base:
        raise RuntimeError(
            "Checkout の戻り先 URL が必要です。"
            " PUBLIC_BASE_URL を設定するか、VERCEL_URL / RENDER_EXTERNAL_URL / RAILWAY_PUBLIC_DOMAIN 等の公開 URL 環境変数を利用してください。"
        )
    if not settings.stripe_secret_key:
        raise RuntimeError("STRIPE_SECRET_KEY が未設定です")

    return await anyio.to_thread.run_sync(_create_checkout_session_sync, settings, base)


def _retrieve_session_sync(session_id: str, secret_key: str) -> Any:
    stripe.api_key = secret_key
    return stripe.checkout.Session.retrieve(session_id)


async def is_checkout_session_paid(session_id: str, settings: Settings) -> bool:
    if not settings.stripe_secret_key:
        return False
    if not (session_id.startswith("cs_test_") or session_id.startswith("cs_live_")):
        return False
    try:
        s = await anyio.to_thread.run_sync(
            _retrieve_session_sync,
            session_id,
            settings.stripe_secret_key,
        )
    except stripe.StripeError:
        return False
    return getattr(s, "payment_status", None) == "paid"
