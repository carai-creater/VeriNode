from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from app.config import Settings, get_settings
from app.stripe_service import create_verify_checkout_session, resolve_checkout_return_base_url

router = APIRouter(prefix="/billing", tags=["billing"])


@router.post("/checkout-session")
async def create_checkout_session(settings: Settings = Depends(get_settings)):
    """支払い用 Stripe Checkout を明示的に発行（402 を経由せず取得したいクライアント向け）。"""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="STRIPE_SECRET_KEY が未設定です")
    if not resolve_checkout_return_base_url(settings):
        raise HTTPException(
            status_code=503,
            detail="STRIPE_CHECKOUT_RETURN_BASE_URL または PUBLIC_BASE_URL、または RENDER_EXTERNAL_URL 等の公開オリジンが必要です",
        )
    try:
        url, sid = await create_verify_checkout_session(settings)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Stripe エラー: {e!s}") from e
    return {"url": url, "checkout_session_id": sid}


@router.get("/success")
async def billing_success(session_id: Optional[str] = Query(None, description="Stripe Checkout Session ID")):
    """Checkout 成功後のランディング（人間向け）。エージェントは session_id を X-Payment-Proof に付与して再試行する。"""
    if not session_id:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "detail": "session_id が必要です"},
        )
    return {
        "ok": True,
        "checkout_session_id": session_id,
        "hint": "API 呼び出し時にヘッダー X-Payment-Proof にこの checkout_session_id を付けてください。",
    }
