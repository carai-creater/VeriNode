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
      --bg: #f5f5f7;
      --surface: #ffffff;
      --text: #1d1d1f;
      --muted: #6e6e73;
      --line: rgba(0, 0, 0, 0.08);
      --link: #0066cc;
      --radius: 18px;
      --font: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display",
        "Hiragino Sans", "Hiragino Kaku Gothic ProN", "Noto Sans JP", system-ui, sans-serif;
      --mono: "SF Mono", ui-monospace, "Cascadia Code", "Consolas", monospace;
      --shell-pad: clamp(1.25rem, 4vw, 2.75rem);
      --shell-max: min(1200px, calc(100% - 2 * var(--shell-pad)));
    }}
    @media (prefers-color-scheme: dark) {{
      :root {{
        --bg: #000000;
        --surface: #1c1c1e;
        --text: #f5f5f7;
        --muted: #a1a1a6;
        --line: rgba(255, 255, 255, 0.12);
        --link: #2997ff;
      }}
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: var(--font);
      color: var(--text);
      background: var(--bg);
      font-size: 17px;
      line-height: 1.47059;
      -webkit-font-smoothing: antialiased;
    }}
    .shell {{
      width: 100%;
      max-width: var(--shell-max);
      margin: 0 auto;
      padding-left: var(--shell-pad);
      padding-right: var(--shell-pad);
    }}
    .topbar {{
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
      background: var(--bg);
      background: color-mix(in srgb, var(--bg) 82%, transparent);
      border-bottom: 1px solid var(--line);
    }}
    .topbar .inner {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem 1.25rem;
      min-height: 3.25rem;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: -0.01em;
    }}
    .topbar nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem 1.1rem;
    }}
    .topbar a {{
      color: var(--muted);
      text-decoration: none;
      white-space: nowrap;
    }}
    .topbar a:hover {{ color: var(--text); }}
    .hero {{
      padding: clamp(3.5rem, 12vw, 6.5rem) 0 clamp(3rem, 8vw, 4.5rem);
      text-align: center;
    }}
    .hero h1 {{
      font-size: clamp(2.5rem, 7vw, 3.75rem);
      font-weight: 600;
      letter-spacing: -0.022em;
      line-height: 1.05;
      margin: 0 0 0.35rem;
    }}
    .hero .ver {{
      display: inline-block;
      font-family: var(--mono);
      font-size: 11px;
      font-weight: 500;
      color: var(--muted);
      letter-spacing: 0.06em;
      margin-bottom: 1rem;
    }}
    .hero .lead {{
      font-size: clamp(1.05rem, 2.2vw, 1.25rem);
      color: var(--muted);
      max-width: 38rem;
      margin: 0 auto 2rem;
      font-weight: 400;
    }}
    .quick {{
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.65rem;
      list-style: none;
      margin: 0;
      padding: 0;
    }}
    .quick a {{
      display: inline-flex;
      align-items: center;
      padding: 0.5rem 1rem;
      font-size: 14px;
      font-weight: 500;
      color: var(--link);
      text-decoration: none;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: var(--surface);
      transition: opacity 0.15s ease;
    }}
    .quick a:hover {{ opacity: 0.75; }}
    .section {{
      padding: clamp(3rem, 7vw, 5rem) 0;
      border-top: 1px solid var(--line);
    }}
    .section-head {{
      font-size: clamp(1.75rem, 4vw, 2.5rem);
      font-weight: 600;
      letter-spacing: -0.019em;
      line-height: 1.1;
      margin: 0 0 1rem;
    }}
    .section-sub {{
      font-size: 19px;
      color: var(--muted);
      max-width: 46rem;
      margin: 0 0 1.75rem;
    }}
    .grid-2 {{
      display: grid;
      grid-template-columns: 1fr;
      gap: clamp(1.5rem, 4vw, 2.5rem);
    }}
    @media (min-width: 900px) {{
      .grid-2 {{ grid-template-columns: 1fr 1fr; gap: 3rem 4rem; }}
    }}
    .card {{
      background: var(--surface);
      border-radius: var(--radius);
      padding: clamp(1.5rem, 3vw, 2rem);
      border: 1px solid var(--line);
    }}
    .card h3 {{
      font-size: 14px;
      font-weight: 600;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      color: var(--muted);
      margin: 0 0 0.75rem;
    }}
    .card p, .card li {{
      font-size: 15px;
      line-height: 1.5;
      color: var(--text);
    }}
    .card p {{ margin: 0 0 0.85rem; }}
    .card p:last-child {{ margin-bottom: 0; }}
    .card ul {{
      margin: 0;
      padding-left: 1.15rem;
      color: var(--muted);
    }}
    .card ul li {{ margin-bottom: 0.4rem; }}
    .price-row {{
      font-size: clamp(1.75rem, 3.5vw, 2.25rem);
      font-weight: 600;
      letter-spacing: -0.02em;
      margin: 0 0 0.5rem;
    }}
    .price-note {{
      font-size: 15px;
      color: var(--muted);
      margin: 0;
    }}
    code, .mono {{
      font-family: var(--mono);
      font-size: 0.9em;
    }}
    code {{
      padding: 0.15em 0.4em;
      border-radius: 6px;
      background: var(--line);
    }}
    table.legal {{
      width: 100%;
      border-collapse: collapse;
      font-size: 15px;
    }}
    table.legal th,
    table.legal td {{
      text-align: left;
      vertical-align: top;
      padding: 0.85rem 0;
      border-bottom: 1px solid var(--line);
    }}
    table.legal tr:last-child th,
    table.legal tr:last-child td {{ border-bottom: none; }}
    table.legal th {{
      width: min(12rem, 32%);
      color: var(--muted);
      font-weight: 500;
      padding-right: 1.25rem;
    }}
    table.legal a {{ color: var(--link); text-decoration: none; }}
    table.legal a:hover {{ text-decoration: underline; }}
    .prose p {{
      font-size: 15px;
      color: var(--muted);
      margin: 0 0 1rem;
      max-width: 52rem;
    }}
    .prose p:last-child {{ margin-bottom: 0; }}
    .prose strong {{ color: var(--text); font-weight: 600; }}
    .prose a {{ color: var(--link); text-decoration: none; }}
    .prose a:hover {{ text-decoration: underline; }}
    .card.prose h3 {{
      font-size: 17px;
      font-weight: 600;
      color: var(--text);
      text-transform: none;
      letter-spacing: -0.01em;
      margin: 0 0 0.65rem;
    }}
    footer.site {{
      padding: 2.5rem 0 4rem;
      border-top: 1px solid var(--line);
      font-size: 12px;
      color: var(--muted);
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="topbar">
    <div class="shell inner">
      <a href="/" style="color:var(--text);font-weight:600;">{SERVICE_NAME}</a>
      <nav aria-label="ページ内">
        <a href="#service">サービス</a>
        <a href="#pricing">料金</a>
        <a href="#payment">決済・返金</a>
        <a href="#legal">特商法</a>
        <a href="#terms">利用規約</a>
        <a href="#privacy">プライバシー</a>
      </nav>
    </div>
  </div>

  <header class="hero">
    <div class="shell">
      <h1>{SERVICE_NAME}</h1>
      <div class="ver">v{APP_VERSION}</div>
      <p class="lead">{SERVICE_TAGLINE}</p>
      <ul class="quick" aria-label="開発者向けリンク">
        <li><a href="/docs">OpenAPI（Swagger）</a></li>
        <li><a href="/.well-known/agent-card.json">A2A agent-card</a></li>
        <li><a href="/.well-known/ai-agent.json">Legacy agent JSON</a></li>
        <li><a href="/health"><span class="mono">GET &#47;health</span></a></li>
      </ul>
    </div>
  </header>

  <main>
    <section id="service" class="section">
      <div class="shell">
        <h2 class="section-head">サービス内容</h2>
        <p class="section-sub">
          本サービスは、プログラムや AI エージェントから HTTP API で利用する<strong>オンラインのファクトチェック（主張の検証）</strong>です。
          お客様が送信した主張テキストを、公開ウェブ検索に基づき分析し、スコア・参照情報・要約などを JSON で返します。
        </p>
        <div class="grid-2">
          <div class="card">
            <h3>提供形態</h3>
            <p>デジタルサービス（API）。物理的な配送はありません。決済完了後、当該リクエストに対する検証結果を即時に返却します。</p>
            <ul>
              <li>主なエンドポイント: <code>POST /verify</code></li>
              <li>未決済時は <code>402</code> と Stripe Checkout への案内（<code>X-Payment-Link</code>）</li>
              <li>エージェント向け記述: <code>/.well-known/agent-card.json</code></li>
            </ul>
          </div>
          <div class="card">
            <h3>表示・審査用情報</h3>
            <p>
              決済処理は <strong>Stripe, Inc.</strong> のセキュアな Checkout を利用します。カード番号等の決済情報は当社サーバーに保存せず、Stripe の方針に従って取り扱われます。
            </p>
            <p style="margin-bottom:0;">
              本ページの<strong>特定商取引法に基づく表記</strong>に、販売事業者名・所在地・連絡先・支払方法・引渡時期・返品条件を記載しています。
            </p>
          </div>
        </div>
      </div>
    </section>

    <section id="pricing" class="section">
      <div class="shell">
        <h2 class="section-head">料金</h2>
        <p class="section-sub">
          日本円（JPY）表示・税込価格です。API 1 回の検証リクエストごとに課金する従量制です。
        </p>
        <div class="card" style="max-width: 36rem;">
          <p class="price-row">¥100（税込）/ 1 リクエスト</p>
          <p class="price-note">
            価格に含まれるもの: 当該リクエストに対するファクトチェック API の利用 1 回分。
            Stripe など決済ネットワーク側で別途手数料が発生する場合は、カード会社等の規約に従います。
          </p>
        </div>
      </div>
    </section>

    <section id="payment" class="section">
      <div class="shell">
        <h2 class="section-head">お支払い・キャンセル・返金</h2>
        <div class="grid-2">
          <div class="card prose">
            <h3>お支払い</h3>
            <p>クレジットカード決済（Stripe）。Checkout 画面の手順に従いお支払いください。決済完了をもって当該分の API 利用が有効になります。</p>
          </div>
          <div class="card prose">
            <h3>キャンセル・返金</h3>
            <p>
              本サービスはデジタルコンテンツ（API による検証結果の提供）です。<strong>検証処理が完了し結果が提供された後の返金・キャンセルはお受けできません。</strong>
              特定商取引法その他の法令により返金が義務付けられる場合は、その限りではありません。
            </p>
            <p>重複課金・決済エラーなど、明らかなシステム上の不具合があった場合は、下記連絡先までご連絡ください。事実関係を確認のうえ対応します。</p>
          </div>
        </div>
      </div>
    </section>

    <section id="legal" class="section">
      <div class="shell">
        <h2 class="section-head">特定商取引法に基づく表記</h2>
        <p class="section-sub">通信販売（デジタルサービス）に関する表示です。</p>
        <div class="card">
          <table class="legal" aria-label="特定商取引法に基づく表記">
            <tbody>
              <tr><th scope="row">運営者名</th><td>林 連太郎</td></tr>
              <tr><th scope="row">所在地</th><td>〒849-0937 佐賀県佐賀市鍋島4丁目2-11 コーポ鍋島２０２</td></tr>
              <tr><th scope="row">連絡先</th><td><a href="mailto:carai@cocarai.com">carai@cocarai.com</a>（お問い合わせはメールにて受け付けます）</td></tr>
              <tr><th scope="row">支払方法</th><td>クレジットカード決済（Stripe）</td></tr>
              <tr><th scope="row">商品の引渡時期</th><td>決済完了後、即時（API 応答として提供）</td></tr>
              <tr><th scope="row">返品</th><td>デジタルコンテンツの特性上、原則として返品不可（上記「キャンセル・返金」を参照）</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="terms" class="section">
      <div class="shell">
        <h2 class="section-head">利用規約（概要）</h2>
        <p class="section-sub">本サービスをご利用いただく前に、以下をご確認ください。詳細な条項が必要な場合は別途文書で定めることがあります。</p>
        <div class="card prose">
          <p><strong>適用</strong>：本規約は、{SERVICE_NAME} ファクトチェック API（以下「本サービス」）の利用に適用されます。</p>
          <p><strong>契約の成立</strong>：お客様が API を利用し、Stripe 経由で料金の支払が完了したとき、当該リクエストについて本サービス提供契約が成立します。</p>
          <p><strong>禁止事項</strong>：法令違反、第三者の権利侵害、当サービスや関連インフラへの不正アクセス・過度な負荷、虚偽の申告、その他運営が不適切と判断する利用を禁止します。</p>
          <p><strong>免責</strong>：検証結果は公開情報に基づく参考情報であり、100% の正確性を保証するものではありません。重大な過失がある場合を除き、間接損害等について責任を負いかねます。詳細は管轄法令の範囲で定めます。</p>
          <p><strong>準拠法・管轄</strong>：日本法を準拠法とし、紛争については運営者所在地を管轄する裁判所を専属的合意管轄とします。</p>
        </div>
      </div>
    </section>

    <section id="privacy" class="section">
      <div class="shell">
        <h2 class="section-head">プライバシー（概要）</h2>
        <p class="section-sub">個人データの取り扱いの要点です。正式なプライバシーポリシーが別途ある場合はそちらを優先します。</p>
        <div class="card prose">
          <p><strong>決済情報</strong>：カード情報等は Stripe が取得・処理します。当社は Stripe が提供する範囲で決済に必要な情報を受け取る場合があります。</p>
          <p><strong>サービス提供</strong>：API に送信された主張テキストは、ファクトチェックのために検索プロバイダ等の外部サービスへ送信される場合があります。ログや課金記録として一定期間技術的に保存されることがあります。</p>
          <p><strong>お問い合わせ</strong>：メールでご連絡いただいた内容は、対応のために保存・利用します。</p>
          <p><strong>開示・訂正・削除</strong>：個人情報保護法その他法令に基づく請求については、<a href="mailto:carai@cocarai.com">carai@cocarai.com</a> までご連絡ください。</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="site">
    <div class="shell">
      <p>{SERVICE_NAME} · Fact-check API · 本サイトは決済・事業者情報の公開用 URL として利用できます。</p>
    </div>
  </footer>
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
