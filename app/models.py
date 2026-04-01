from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    claim: str = Field(..., min_length=1, max_length=4000, description="検証したい主張・事実")


class SourceDetail(BaseModel):
    name: str = Field(..., description="サイト名またはドメイン")
    url: str
    credibility: float = Field(..., ge=0.0, le=1.0, description="当該ソースの信頼度")
    reason: str = Field(..., description="信頼度の根拠（短い説明）")


class VerifyResponse(BaseModel):
    status: str = Field(
        ...,
        description="verified / unverified / payment_required（未払いで決済案内を返すとき）",
    )
    score: float = Field(..., ge=0.0, le=1.0, description="参照ソース信頼度の平均（小数第2位まで）")
    sources: list[str] = Field(default_factory=list)
    source_details: list[SourceDetail] = Field(
        default_factory=list,
        description="支払い証明が有効な場合のみ各ソースの信頼度内訳（それ以外は空）",
    )
    reason: str = Field(..., description="根拠の要約、または決済案内テキスト（URL を含む場合あり）")
    checkout_url: Optional[str] = Field(
        default=None,
        description="status が payment_required のときの決済ページ URL（Stripe 利用時は Checkout Session の url をそのまま）",
    )
    checkout_session_id: Optional[str] = Field(
        default=None,
        description="status が payment_required かつ Stripe 利用時の Checkout Session ID（cs_...）。再試行時 X-Payment-Proof 用。決済リンクの組み立てには使わない",
    )
