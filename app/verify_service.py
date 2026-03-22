"""Web search を用いた簡易ファクトチェック（ヒューリスティック）。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import Settings, get_settings

SERPER_URL = "https://google.serper.dev/search"
GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"

_STOP = frozenset(
    """
    a an the is are was were be been being to of and or for in on at by from as with
    it its this that these those not no yes all any some more most other such than
    then so if about into through during before after above below between under again
    further once here there when where why how both each few most own same so than
    too very can will just don should now である です ます など および ため の を は が に で と も
    """.split()
)


def _tokenize(text: str) -> set[str]:
    lowered = text.lower()
    lowered = re.sub(r"[^\w\s\u3040-\u30ff\u4e00-\u9fff]", " ", lowered, flags=re.UNICODE)
    parts = lowered.split()
    out: set[str] = set()
    for p in parts:
        if len(p) < 2 or p in _STOP:
            continue
        out.add(p)
    return out


def _overlap_score(claim_tokens: set[str], blob: str) -> float:
    if not claim_tokens:
        return 0.3
    blob_tokens = _tokenize(blob)
    if not blob_tokens:
        return 0.0
    inter = len(claim_tokens & blob_tokens)
    return min(1.0, inter / max(1, len(claim_tokens)) * 1.4)


@dataclass
class SearchHit:
    title: str
    snippet: str
    link: str


async def _serper_search(client: httpx.AsyncClient, query: str, settings: Settings) -> list[SearchHit]:
    if not settings.serper_api_key:
        raise RuntimeError("SERPER_API_KEY が未設定です")
    r = await client.post(
        SERPER_URL,
        headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
        json={"q": query, "num": settings.search_num_results},
        timeout=30.0,
    )
    r.raise_for_status()
    data = r.json()
    organic = data.get("organic") or []
    hits: list[SearchHit] = []
    for item in organic:
        link = item.get("link") or ""
        if not link:
            continue
        hits.append(
            SearchHit(
                title=item.get("title") or "",
                snippet=item.get("snippet") or "",
                link=link,
            )
        )
    return hits


async def _google_cse_search(client: httpx.AsyncClient, query: str, settings: Settings) -> list[SearchHit]:
    if not settings.google_cse_api_key or not settings.google_cse_cx:
        raise RuntimeError("GOOGLE_CSE_API_KEY と GOOGLE_CSE_CX が必要です")
    params = {
        "key": settings.google_cse_api_key,
        "cx": settings.google_cse_cx,
        "q": query,
        "num": min(settings.search_num_results, 10),
    }
    r = await client.get(GOOGLE_CSE_URL, params=params, timeout=30.0)
    r.raise_for_status()
    data = r.json()
    items = data.get("items") or []
    hits: list[SearchHit] = []
    for item in items:
        link = item.get("link") or ""
        if not link:
            continue
        hits.append(
            SearchHit(
                title=item.get("title") or "",
                snippet=item.get("htmlSnippet") or item.get("snippet") or "",
                link=link,
            )
        )
    return hits


async def fetch_search_hits(client: httpx.AsyncClient, query: str, settings: Settings | None = None) -> list[SearchHit]:
    s = settings or get_settings()
    if s.serper_api_key:
        return await _serper_search(client, query, s)
    return await _google_cse_search(client, query, s)


def score_claim_against_hits(claim: str, hits: list[SearchHit], threshold: float) -> tuple[float, str, list[str]]:
    claim_tokens = _tokenize(claim)
    if not hits:
        return 0.0, "検索結果が得られず、外部ソースとの照合ができませんでした。", []

    per: list[float] = []
    sources: list[str] = []
    for h in hits[:12]:
        blob = f"{h.title} {h.snippet}"
        per.append(_overlap_score(claim_tokens, blob))
        sources.append(h.link)

    # 複数ソースで類似スコアが揃うほど信頼度を少し上げる
    base = sum(per) / len(per) if per else 0.0
    spread_bonus = 0.0
    if len(per) >= 3:
        hi = max(per)
        if hi >= 0.35:
            spread_bonus = min(0.15, (len([p for p in per if p >= 0.25]) / len(per)) * 0.12)

    score = max(0.0, min(1.0, base + spread_bonus))
    status = "verified" if score >= threshold else "unverified"

    top = sorted(zip(per, hits), key=lambda x: x[0], reverse=True)[:3]
    snippets = [f"{h.title[:80]}…" if len(h.title) > 80 else h.title for _, h in top if h.title]
    if snippets:
        reason = (
            f"検索結果{len(hits)}件を参照。上位ソースとの語句一致度から総合スコア {score:.2f}。"
            f" 代表タイトル: {', '.join(snippets[:2])}。"
        )
    else:
        reason = f"検索結果{len(hits)}件を参照しスコア {score:.2f} を算出。"

    return score, reason.strip(), sources


async def verify_claim(claim: str, client: httpx.AsyncClient, settings: Settings | None = None) -> dict[str, Any]:
    s = settings or get_settings()
    stripped = claim.strip()
    query = stripped if len(stripped) < 240 else stripped[:240]
    hits = await fetch_search_hits(client, query, s)
    score, reason, sources = score_claim_against_hits(stripped, hits, s.verify_score_threshold)
    status = "verified" if score >= s.verify_score_threshold else "unverified"
    return {"status": status, "score": round(score, 4), "sources": sources, "reason": reason}
