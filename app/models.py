from __future__ import annotations

from pydantic import BaseModel, Field


class VerifyRequest(BaseModel):
    claim: str = Field(..., min_length=1, max_length=4000, description="検証したい主張・事実")


class VerifyResponse(BaseModel):
    status: str = Field(..., description="verified または unverified")
    score: float = Field(..., ge=0.0, le=1.0)
    sources: list[str] = Field(default_factory=list)
    reason: str = Field(..., description="根拠の要約")
