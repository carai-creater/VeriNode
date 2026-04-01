"""支払い証明の検証（静的トークン or Stripe Checkout セッション）。"""

from __future__ import annotations

from typing import Optional

from app.config import Settings
from app.stripe_service import is_checkout_session_paid


async def is_payment_proof_valid(proof: Optional[str], settings: Settings) -> bool:
    if not proof or not str(proof).strip():
        return False
    p = str(proof).strip()
    if settings.verify_payment_token and p == settings.verify_payment_token:
        print("Payment status: accepted (verify_payment_token)", flush=True)
        return True
    if settings.stripe_secret_key and (p.startswith("cs_test_") or p.startswith("cs_live_")):
        return await is_checkout_session_paid(p, settings)
    print("Payment status: rejected (unrecognized proof)", flush=True)
    return False
