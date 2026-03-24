from __future__ import annotations

from typing import AsyncIterator

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware

from app.agent_card import build_a2a_agent_card, build_agent_card
from app.branding import APP_VERSION, SERVICE_NAME, SERVICE_TAGLINE
from app.config import Settings, get_settings
from app.middleware.payment import PaymentRequiredMiddleware
from app.models import VerifyRequest, VerifyResponse
from app.routers import billing, webhooks
from app.verify_service import verify_claim

app = FastAPI(
    title=f"{SERVICE_NAME} — Fact-check API",
    description=SERVICE_TAGLINE,
    version=APP_VERSION,
)

app.add_middleware(PaymentRequiredMiddleware)
app.include_router(billing.router)
app.include_router(webhooks.router)


async def get_http_client() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient() as client:
        yield client


@app.get("/health")
async def health():
    return {"ok": True}


def _root_page_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="color-scheme" content="light dark" />
  <title>{SERVICE_NAME} · Fact-check API</title>
  <style>
    :root {{
      --bg: #f4f5f7;
      --surface: #ffffff;
      --text: #111318;
      --muted: #5c6370;
      --line: rgba(17, 19, 24, 0.08);
      --accent: #0f766e;
      --accent-soft: rgba(15, 118, 110, 0.12);
      --radius: 12px;
      --font: ui-sans-serif, system-ui, -apple-system, "Segoe UI", "Hiragino Sans",
        "Hiragino Kaku Gothic ProN", "Noto Sans JP", sans-serif;
      --mono: ui-monospace, "SF Mono", "Cascadia Code", "Consolas", monospace;
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #0c0e12;
        --surface: #14171d;
        --text: #e8eaef;
        --muted: #9aa3b2;
        --line: rgba(232, 234, 239, 0.1);
        --accent: #2dd4bf;
        --accent-soft: rgba(45, 212, 191, 0.15);
      }}
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: var(--font);
      color: var(--text);
      background: var(--bg);
      line-height: 1.6;
      font-size: 15px;
      -webkit-font-smoothing: antialiased;
    }}
    .wrap {{
      max-width: 44rem;
      margin: 0 auto;
      padding: clamp(2rem, 5vw, 3.25rem) 1.25rem 4rem;
    }}
    .hero {{
      margin-bottom: 2rem;
    }}
    .brand {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 0.65rem 0.85rem;
      margin-bottom: 0.5rem;
    }}
    h1 {{
      font-size: clamp(1.35rem, 3.5vw, 1.65rem);
      font-weight: 650;
      letter-spacing: -0.03em;
      margin: 0;
      line-height: 1.2;
    }}
    .ver {{
      font-family: var(--mono);
      font-size: 0.72rem;
      font-weight: 500;
      letter-spacing: 0.02em;
      color: var(--muted);
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
      background: var(--line);
    }}
    .lead {{
      color: var(--muted);
      font-size: 0.92rem;
      margin: 0;
      max-width: 36em;
    }}
    .quick {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin: 1.35rem 0 0;
      padding: 0;
      list-style: none;
    }}
    .quick a {{
      display: inline-flex;
      align-items: center;
      gap: 0.35rem;
      font-size: 0.8125rem;
      font-weight: 500;
      color: var(--accent);
      text-decoration: none;
      padding: 0.4rem 0.75rem;
      border-radius: 999px;
      background: var(--accent-soft);
      transition: transform 0.12s ease, opacity 0.12s ease;
    }}
    .quick a:hover {{ opacity: 0.92; transform: translateY(-1px); }}
    .panel {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      padding: 1.25rem 1.35rem 1.1rem;
      margin-bottom: 1rem;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }}
    @media (prefers-color-scheme: dark) {{
      .panel {{ box-shadow: none; }}
    }}
    h2 {{
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
      margin: 0 0 0.85rem;
    }}
    p {{ margin: 0 0 0.85rem; }}
    p:last-child {{ margin-bottom: 0; }}
    ul.api {{
      margin: 0;
      padding-left: 1.1rem;
      color: var(--muted);
      font-size: 0.9rem;
    }}
    ul.api li {{ margin-bottom: 0.45rem; }}
    ul.api li:last-child {{ margin-bottom: 0; }}
    code {{
      font-family: var(--mono);
      font-size: 0.84em;
      padding: 0.12em 0.38em;
      border-radius: 5px;
      background: var(--line);
      color: var(--text);
    }}
    .price {{
      font-family: var(--mono);
      font-size: 1rem;
      font-weight: 600;
      color: var(--text);
      letter-spacing: -0.02em;
    }}
    .note {{
      font-size: 0.875rem;
      color: var(--muted);
    }}
    table.legal {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.875rem;
    }}
    table.legal th,
    table.legal td {{
      text-align: left;
      vertical-align: top;
      padding: 0.55rem 0;
      border-bottom: 1px solid var(--line);
    }}
    table.legal tr:last-child th,
    table.legal tr:last-child td {{
      border-bottom: none;
    }}
    table.legal th {{
      width: 9.5rem;
      color: var(--muted);
      font-weight: 500;
      padding-right: 0.75rem;
    }}
    table.legal a {{ color: var(--accent); text-decoration: none; }}
    table.legal a:hover {{ text-decoration: underline; }}
    footer {{
      margin-top: 1.75rem;
      font-size: 0.8rem;
      color: var(--muted);
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="hero">
      <div class="brand">
        <h1>{SERVICE_NAME}</h1>
        <span class="ver">v{APP_VERSION}</span>
      </div>
      <p class="lead">{SERVICE_TAGLINE}</p>
      <ul class="quick" aria-label="開発者リンク">
        <li><a href="/docs">OpenAPI / Swagger</a></li>
        <li><a href="/.well-known/agent-card.json">A2A agent-card</a></li>
        <li><a href="/.well-known/ai-agent.json">Legacy agent JSON</a></li>
        <li><a href="/health"><code>/health</code></a></li>
      </ul>
    </header>

    <section class="panel" aria-labelledby="api-h">
      <h2 id="api-h">API</h2>
      <p>Web 検索に基づく主張検証。エージェントやバックエンドから <code>POST /verify</code>（JSON）で呼び出します。</p>
      <ul class="api">
        <li>レスポンス: スコア・根拠ソース・要約</li>
        <li>課金: 未払い時は <code>402 Payment Required</code>、<code>X-Payment-Link</code> から Stripe Checkout</li>
        <li>ディスカバリ: <code>/.well-known/agent-card.json</code>（A2A）</li>
      </ul>
    </section>

    <section class="panel" aria-labelledby="price-h">
      <h2 id="price-h">Pricing</h2>
      <p class="price">¥100 / request（税込）</p>
      <p class="note">Stripe カード決済。ゲート通過後に API が利用可能になります。</p>
    </section>

    <section class="panel" aria-labelledby="legal-h">
      <h2 id="legal-h">特定商取引法に基づく表記</h2>
      <table class="legal" aria-label="特定商取引法に基づく表記">
        <tbody>
          <tr><th scope="row">運営者名</th><td>林 連太郎</td></tr>
          <tr><th scope="row">所在地</th><td>〒849-0937 佐賀県佐賀市鍋島4丁目2-11 コーポ鍋島２０２</td></tr>
          <tr><th scope="row">連絡先</th><td><a href="mailto:carai@cocarai.com">carai@cocarai.com</a></td></tr>
          <tr><th scope="row">支払方法</th><td>クレジットカード決済（Stripe）</td></tr>
          <tr><th scope="row">商品の引渡時期</th><td>決済完了後、即時</td></tr>
          <tr><th scope="row">返品</th><td>デジタルコンテンツの特性上、返品不可</td></tr>
        </tbody>
      </table>
    </section>

    <footer>
      <p>{SERVICE_NAME} — Fact-check API</p>
    </footer>
  </div>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return HTMLResponse(content=_root_page_html())


@app.get("/.well-known/ai-agent.json", include_in_schema=False)
async def ai_agent_card(request: Request, settings: Settings = Depends(get_settings)):
    """他エージェント向けの能力・認証・エンドポイント記述。"""
    return build_agent_card(request, settings)


@app.get("/.well-known/agent-card.json", include_in_schema=False)
async def a2a_well_known_agent_card(request: Request, settings: Settings = Depends(get_settings)):
    """[Google A2A](https://github.com/google/A2A) の Well-Known Agent Card（discovery 用）。"""
    data = build_a2a_agent_card(request, settings)
    return JSONResponse(
        content=data,
        headers={
            "Cache-Control": "public, max-age=300",
        },
    )


@app.post("/verify", response_model=VerifyResponse)
async def verify(
    body: VerifyRequest,
    client: httpx.AsyncClient = Depends(get_http_client),
    settings: Settings = Depends(get_settings),
) -> VerifyResponse:
    if not settings.serper_api_key and (not settings.google_cse_api_key or not settings.google_cse_cx):
        raise HTTPException(
            status_code=503,
            detail="検索プロバイダが未設定です。SERPER_API_KEY または GOOGLE_CSE_API_KEY + GOOGLE_CSE_CX を設定してください。",
        )
    try:
        result = await verify_claim(body.claim, client, settings)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"検索 API エラー: {e.response.status_code}") from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    return VerifyResponse(**result)


def _configure_cors(application: FastAPI) -> None:
    raw = get_settings().cors_allow_origins
    if not raw:
        return
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    if not origins:
        return
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Payment-Link", "X-Payment-Proof"],
    )


_configure_cors(app)
