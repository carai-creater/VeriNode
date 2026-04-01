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


def resolve_checkout_return_base_url(settings: Settings) -> Optional[str]:
    """Stripe Checkout の success_url / cancel_url に使うオリジン（https 推奨）。"""
    if settings.stripe_checkout_return_base_url:
        return settings.stripe_checkout_return_base_url.rstrip("/")
    return resolve_public_base_url(settings)


def _create_checkout_session_sync(settings: Settings, base_url: str) -> Tuple[str, str]:
    stripe.api_key = settings.stripe_secret_key
    # Stripe の success_url にはリダイレクト時に {CHECKOUT_SESSION_ID} が置換される（リテラルで渡す）
    success = f"{base_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel = f"{base_url}/?payment=canceled"

    if settings.stripe_price_id:
        line_items: list[dict[str, Any]] = [{"price": settings.stripe_price_id, "quantity": 1}]
    else:
        unit = int(settings.stripe_verify_unit_amount_jpy)
        line_items = [
            {
                "price_data": {
                    "currency": "jpy",
                    "product_data": {
                        "name": f"{SERVICE_NAME} — verification credit",
                        "description": "Single fact-check / verify API call credit (pay-per-use).",
                    },
                    "unit_amount": unit,
                },
                "quantity": 1,
            }
        ]

    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=line_items,
        success_url=success,
        cancel_url=cancel,
        metadata={"product": "verinode_verify", "service": SERVICE_NAME},
    )
    url = session.url or ""
    sid = session.id
    if not url:
        raise RuntimeError("Stripe Checkout Session に url がありません")
    amount_note = (
        f"stripe_price_id={settings.stripe_price_id}"
        if settings.stripe_price_id
        else f"unit_amount_jpy={int(settings.stripe_verify_unit_amount_jpy)}"
    )
    print(
        "[stripe] Checkout Session created",
        "mode=payment",
        amount_note,
        f"session_id={sid}",
        f"success_url={success}",
        f"cancel_url={cancel}",
        f"checkout_url={url}",
        flush=True,
    )
    return url, sid


async def create_verify_checkout_session(settings: Settings) -> Tuple[str, str]:
    base = resolve_checkout_return_base_url(settings)
    if not base:
        raise RuntimeError(
            "Checkout の戻り先 URL が必要です。"
            " STRIPE_CHECKOUT_RETURN_BASE_URL（例: https://verinode.onrender.com）または"
            " PUBLIC_BASE_URL / VERCEL_URL / RENDER_EXTERNAL_URL / RAILWAY_PUBLIC_DOMAIN を設定してください。"
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
