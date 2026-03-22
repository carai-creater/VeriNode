from __future__ import annotations

from typing import AsyncIterator

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

from app.agent_card import build_agent_card
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
  <title>VeriNode - AIエージェント向けファクトチェックAPI</title>
  <style>
    :root {{
      --text: #1a1a1a;
      --muted: #5c5c5c;
      --border: #e8e8ec;
      --bg: #fafbfc;
      --accent: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Noto Sans JP", Meiryo, sans-serif;
      color: var(--text);
      background: var(--bg);
      line-height: 1.65;
      font-size: 16px;
    }}
    .wrap {{
      max-width: 40rem;
      margin: 0 auto;
      padding: 2.5rem 1.5rem 4rem;
    }}
    h1 {{
      font-size: 1.5rem;
      font-weight: 600;
      letter-spacing: -0.02em;
      margin: 0 0 0.35rem;
      line-height: 1.3;
    }}
    .lead {{
      color: var(--muted);
      font-size: 0.95rem;
      margin: 0 0 2rem;
    }}
    h2 {{
      font-size: 1.05rem;
      font-weight: 600;
      margin: 2.25rem 0 0.75rem;
      padding-bottom: 0.35rem;
      border-bottom: 1px solid var(--border);
    }}
    p {{ margin: 0 0 1rem; }}
    .price {{
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--text);
    }}
    table.legal {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.95rem;
      margin-top: 0.5rem;
    }}
    table.legal th,
    table.legal td {{
      text-align: left;
      vertical-align: top;
      padding: 0.65rem 0;
      border-bottom: 1px solid var(--border);
    }}
    table.legal th {{
      width: 11rem;
      color: var(--muted);
      font-weight: 500;
      padding-right: 1rem;
    }}
    footer {{
      margin-top: 3rem;
      padding-top: 1.5rem;
      border-top: 1px solid var(--border);
      font-size: 0.85rem;
      color: var(--muted);
    }}
    footer a {{ color: var(--accent); text-decoration: none; }}
    footer a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <div class="wrap">
    <h1>VeriNode - AIエージェント向けファクトチェックAPI</h1>
    <p class="lead">{SERVICE_NAME} — {SERVICE_TAGLINE}</p>

    <h2>サービス概要</h2>
    <p>
      本サービスは、AI エージェントおよびプログラムから HTTP API 経由で利用できる
      <strong>ファクトチェック（主張の検証）API</strong>です。
      ウェブ検索に基づき、入力された主張に対するスコア・参照ソース・要約を返します。
    </p>

    <h2>価格</h2>
    <p class="price">1 リクエストあたり 100 円（税込）</p>
    <p style="color: var(--muted); font-size: 0.9rem;">
      お支払いは Stripe によるクレジットカード決済です。API 利用時に課金ゲート（HTTP 402）より Checkout に進みます。
    </p>

    <h2>特定商取引法に基づく表記</h2>
    <table class="legal" aria-label="特定商取引法に基づく表記">
      <tbody>
        <tr><th scope="row">運営者名</th><td>林 連太郎</td></tr>
        <tr><th scope="row">所在地</th><td>〒849-0937 佐賀県佐賀市鍋島4丁目2-11 cope nabeshima202</td></tr>
        <tr><th scope="row">連絡先</th><td><a href="mailto:carai@cocarai.com">carai@cocarai.com</a></td></tr>
        <tr><th scope="row">支払方法</th><td>クレジットカード決済（Stripe）</td></tr>
        <tr><th scope="row">商品の引渡時期</th><td>決済完了後、即時</td></tr>
        <tr><th scope="row">返品</th><td>デジタルコンテンツの特性上、返品不可</td></tr>
      </tbody>
    </table>

    <footer>
      <p>開発者向け: <a href="/docs">API ドキュメント（Swagger）</a> ·
      <a href="/.well-known/ai-agent.json">エージェントカード（JSON）</a> ·
      <a href="/health">ヘルスチェック</a></p>
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
