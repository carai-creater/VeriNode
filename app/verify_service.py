"""Web search とドメイン・オーソリティに基づくファクトチェック。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Optional
from urllib.parse import urlparse

import httpx

from app.config import Settings, get_settings

SERPER_URL = "https://google.serper.dev/search"
GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"

# ドメイン → (信頼度 0.0–1.0, 説明のベース)
SOURCE_TIERS: dict[str, tuple[float, str]] = {
    # Tier 1 — 公式・通信社
    "reuters.com": (1.0, "国際的通信社（Tier 1）のため最高信頼"),
    "apnews.com": (1.0, "国際的通信社（Tier 1）のため最高信頼"),
    "bbc.com": (1.0, "主要公式メディア（Tier 1）のため最高信頼"),
    "bbc.co.uk": (1.0, "主要公式メディア（Tier 1）のため最高信頼"),
    "nikkei.com": (1.0, "主要経済メディア（Tier 1）のため最高信頼"),
    "bloomberg.com": (1.0, "主要経済メディア（Tier 1）のため最高信頼"),
    "nytimes.com": (1.0, "主要公式メディア（Tier 1）のため最高信頼"),
    # Tier 2 — 専門大手メディア
    "theverge.com": (0.8, "専門大手テックメディア（Tier 2）のため高信頼"),
    "techcrunch.com": (0.8, "専門大手テックメディア（Tier 2）のため高信頼"),
    "wired.com": (0.8, "専門大手テックメディア（Tier 2）のため高信頼"),
    "9to5mac.com": (0.8, "専門大手テックメディア（Tier 2）のため高信頼"),
    "bgr.com": (0.8, "専門大手テックメディア（Tier 2）のため高信頼"),
    # Tier 3 — 一般テック・経済
    "wsj.com": (0.5, "一般経済紙（Tier 3）／要約ソースとして中程度の信頼"),
    "engadget.com": (0.5, "一般テックメディア（Tier 3）のため中程度の信頼"),
    "gizmodo.com": (0.5, "一般テックメディア（Tier 3）のため中程度の信頼"),
    # Tier 4 — SNS・個人
    "twitter.com": (0.2, "SNS・コミュニティ（Tier 4）のため低信頼"),
    "x.com": (0.2, "SNS・コミュニティ（Tier 4）のため低信頼"),
    "reddit.com": (0.2, "SNS・コミュニティ（Tier 4）のため低信頼"),
}


def _normalize_hostname(url: str) -> str:
    raw = (url or "").strip()
    if not raw:
        return ""
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
        raw = "https://" + raw
    try:
        host = (urlparse(raw).hostname or "").lower()
    except Exception:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def _match_tier(hostname: str) -> Optional[tuple[float, str, str]]:
    """マッチしたら (credibility, reason, display_domain)。"""
    if not hostname:
        return None
    for domain in sorted(SOURCE_TIERS.keys(), key=len, reverse=True):
        if hostname == domain or hostname.endswith("." + domain):
            cred, desc = SOURCE_TIERS[domain]
            return (cred, desc, domain)
    return None


def _suffix_trust(hostname: str) -> Optional[tuple[float, str]]:
    """.gov / .edu / .org 系（登録済みドメインに無い場合の補助ルール）。"""
    h = hostname.lower()
    if h.endswith(".gov") or h.endswith(".gov.uk") or h.endswith(".gov.au"):
        return (0.9, "政府機関ドメイン（.gov 系）のため高信頼")
    if h.endswith(".edu") or h.endswith(".edu.au"):
        return (0.9, "教育機関ドメイン（.edu 系）のため高信頼")
    if h.endswith(".org") or h.endswith(".org.uk"):
        return (0.9, "非営利団体ドメイン（.org 系）のため高信頼")
    return None


def credibility_for_url(url: str) -> tuple[float, str, str]:
    """
    参照 URL の信頼度を返す。
    戻り値: (credibility, reason, name) — name は表示用（ドメイン中心）。
    """
    hostname = _normalize_hostname(url)
    if not hostname:
        return (0.0, "URL を解釈できませんでした。", "unknown")

    tier = _match_tier(hostname)
    if tier:
        cred, reason, _domain = tier
        return (cred, reason, hostname)

    suffix = _suffix_trust(hostname)
    if suffix:
        cred, reason = suffix
        return (cred, reason, hostname)

    print(f"Unknown domain, default score applied: {hostname}", flush=True)
    return (0.3, "辞書未登録のドメインのためデフォルト信頼度（0.3）を適用", hostname)


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


def score_claim_by_source_authority(
    hits: list[SearchHit],
    include_source_details: bool,
) -> tuple[float, str, list[str], list[dict[str, Any]]]:
    """
    参照ソースのドメイン信頼度の平均をスコアとする。
    source_details は include_source_details が True のときのみ中身を詰める。
    """
    if not hits:
        return (
            0.0,
            "検索結果が得られず、外部ソースとの照合ができませんでした。",
            [],
            [],
        )

    used = hits[:12]
    creds: list[float] = []
    sources: list[str] = []
    details: list[dict[str, Any]] = []

    for h in used:
        cred, reason, name = credibility_for_url(h.link)
        creds.append(cred)
        sources.append(h.link)
        display_name = name
        if h.title.strip():
            display_name = h.title.strip()[:120]
        if include_source_details:
            details.append(
                {
                    "name": display_name,
                    "url": h.link,
                    "credibility": round(cred, 2),
                    "reason": reason,
                }
            )

    score = sum(creds) / len(creds) if creds else 0.0
    score = round(score, 2)
    top_titles = [h.title[:50] + "…" if len(h.title) > 50 else h.title for h in used[:2] if h.title]
    if top_titles:
        reason = (
            f"検索結果{len(hits)}件を参照。上位ソースのドメイン信頼度の平均をスコア {score:.2f} としました。"
            f" 代表: {', '.join(top_titles[:2])}。"
        )
    else:
        reason = f"検索結果{len(hits)}件を参照し、ドメイン信頼度の平均スコア {score:.2f} を算出しました。"

    return score, reason.strip(), sources, details


async def verify_claim(
    claim: str,
    client: httpx.AsyncClient,
    settings: Settings | None = None,
    *,
    include_source_details: bool = False,
) -> dict[str, Any]:
    s = settings or get_settings()
    stripped = claim.strip()
    query = stripped if len(stripped) < 240 else stripped[:240]
    hits = await fetch_search_hits(client, query, s)
    score, reason, sources, details = score_claim_by_source_authority(hits, include_source_details)
    status = "verified" if score >= s.verify_score_threshold else "unverified"
    out: dict[str, Any] = {
        "status": status,
        "score": score,
        "sources": sources,
        "reason": reason,
    }
    if include_source_details:
        out["source_details"] = details
    else:
        out["source_details"] = []
    return out
