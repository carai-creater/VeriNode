from __future__ import annotations

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import Settings, get_settings

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request, settings: Settings = Depends(get_settings)):
    """Stripe からのイベント（署名検証）。将来のクレジット台帳・メーター課金のフック用。"""
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="STRIPE_WEBHOOK_SECRET が未設定です")

    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    if not sig:
        raise HTTPException(status_code=400, detail="stripe-signature ヘッダーがありません")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig,
            settings.stripe_webhook_secret,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e!s}") from e
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="署名が無効です") from e

    if event.get("type") == "checkout.session.completed":
        # TODO: 永続ストアに購入を記録し、API キー／クレジットと紐づける場合はここで処理
        pass

    return {"received": True, "type": event.get("type"), "id": event.get("id")}
