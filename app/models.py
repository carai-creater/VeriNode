from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    claim: str = Field(..., min_length=1, max_length=4000, description="検証したい主張・事実")


class VerifyResponse(BaseModel):
    status: str = Field(
        ...,
        description="verified / unverified / payment_required（未払いで決済案内を返すとき）",
    )
    score: float = Field(..., ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    reason: str = Field(..., description="根拠の要約、または決済案内テキスト（URL を含む場合あり）")
    checkout_url: Optional[str] = Field(
        default=None,
        description="status が payment_required のときの決済ページ URL（Stripe 利用時は Checkout Session の url をそのまま）",
    )
    checkout_session_id: Optional[str] = Field(
        default=None,
        description="status が payment_required かつ Stripe 利用時の Checkout Session ID（cs_...）。再試行時 X-Payment-Proof 用。決済リンクの組み立てには使わない",
    )
