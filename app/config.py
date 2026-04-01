from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Optional, Tuple

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_files_for_pydantic() -> Tuple[str, ...]:
    """
    本番・ホステッド環境ではプロセスの環境変数のみを使う（.env を読まない）。
    - Vercel では VERCEL=1 が自動設定される → .env を参照しない。
    - 意図的に無効化: DISABLE_DOTENV=1
    ローカルでは .env があれば読み込む（ファイルが無ければ無視）。
    """
    if os.getenv("VERCEL"):
        return ()
    if os.getenv("DISABLE_DOTENV", "").strip().lower() in ("1", "true", "yes", "on"):
        return ()
    return (".env",)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files_for_pydantic(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    serper_api_key: Optional[str] = Field(default=None, validation_alias="SERPER_API_KEY")
    google_cse_api_key: Optional[str] = Field(default=None, validation_alias="GOOGLE_CSE_API_KEY")
    google_cse_cx: Optional[str] = Field(default=None, validation_alias="GOOGLE_CSE_CX")

    # 本番で課金を強制する場合は false（.env で VERIFY_SKIP_PAYMENT=0）
    verify_skip_payment: bool = Field(default=True, validation_alias="VERIFY_SKIP_PAYMENT")

    @field_validator("verify_skip_payment", mode="before")
    @classmethod
    def _parse_skip_payment(cls, v: Any) -> bool:
        if v is None or v == "":
            return False
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(int(v))
        s = str(v).strip().lower()
        return s in ("1", "true", "yes", "on")
    payment_link_url: str = Field(
        default="https://example.com/pay",
        validation_alias="PAYMENT_LINK_URL",
    )
    verify_payment_token: Optional[str] = Field(default=None, validation_alias="VERIFY_PAYMENT_TOKEN")

    # Stripe（設定時は未払い POST /verify が 200 + payment_required で Checkout URL を返し、支払済み cs_... を X-Payment-Proof で受け付ける）
    stripe_secret_key: Optional[str] = Field(default=None, validation_alias="STRIPE_SECRET_KEY")
    stripe_webhook_secret: Optional[str] = Field(default=None, validation_alias="STRIPE_WEBHOOK_SECRET")
    stripe_price_id: Optional[str] = Field(default=None, validation_alias="STRIPE_PRICE_ID")
    stripe_verify_unit_amount_jpy: int = Field(
        default=100,
        ge=1,
        validation_alias="STRIPE_VERIFY_UNIT_AMOUNT_JPY",
        description="Stripe price_data.unit_amount（JPY は円単位の整数。例: 100）",
    )
    public_base_url: Optional[str] = Field(
        default=None,
        validation_alias="PUBLIC_BASE_URL",
        description="公開オリジン（API ドキュメント・リダイレクト解決など）",
    )
    stripe_checkout_return_base_url: Optional[str] = Field(
        default=None,
        validation_alias="STRIPE_CHECKOUT_RETURN_BASE_URL",
        description=(
            "Stripe Checkout の success_url / cancel_url のオリジン（例: https://verinode.onrender.com）。"
            "未設定時は PUBLIC_BASE_URL または RENDER_EXTERNAL_URL 等と同じ解決ロジック。"
        ),
    )

    verify_score_threshold: float = Field(default=0.62, ge=0.0, le=1.0, validation_alias="VERIFY_SCORE_THRESHOLD")

    search_num_results: int = Field(default=8, ge=1, le=20)

    # カンマ区切り。ブラウザから別オリジンで /verify や 402 の X-Payment-Link を読むときに設定
    cors_allow_origins: Optional[str] = Field(default=None, validation_alias="CORS_ALLOW_ORIGINS")

    @field_validator(
        "verify_payment_token",
        "stripe_secret_key",
        "public_base_url",
        "stripe_webhook_secret",
        "stripe_price_id",
        "stripe_checkout_return_base_url",
        "cors_allow_origins",
        mode="before",
    )
    @classmethod
    def _strip_optional_str(cls, v: Any) -> Any:
        if v is None:
            return None
        if isinstance(v, str):
            s = v.strip()
            return s or None
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
