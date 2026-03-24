"""Marketing / legal landing HTML (Japanese and English)."""

from __future__ import annotations

from app.branding import APP_VERSION, SERVICE_NAME, SERVICE_TAGLINE

SERVICE_TAGLINE_EN = (
    "Web-grounded fact-checking and payment gating for AI agents and backends."
)

# Shared layout CSS (single `{` — not an f-string).
LANDING_CSS = """
    :root {
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
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --bg: #000000;
        --surface: #1c1c1e;
        --text: #f5f5f7;
        --muted: #a1a1a6;
        --line: rgba(255, 255, 255, 0.12);
        --link: #2997ff;
      }
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      font-family: var(--font);
      color: var(--text);
      background: var(--bg);
      font-size: 17px;
      line-height: 1.47059;
      -webkit-font-smoothing: antialiased;
    }
    .shell {
      width: 100%;
      max-width: var(--shell-max);
      margin: 0 auto;
      padding-left: var(--shell-pad);
      padding-right: var(--shell-pad);
    }
    .topbar {
      position: sticky;
      top: 0;
      z-index: 10;
      backdrop-filter: saturate(180%) blur(20px);
      -webkit-backdrop-filter: saturate(180%) blur(20px);
      background: var(--bg);
      background: color-mix(in srgb, var(--bg) 82%, transparent);
      border-bottom: 1px solid var(--line);
    }
    .topbar .inner {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem 1.25rem;
      min-height: 3.25rem;
      font-size: 12px;
      font-weight: 500;
      letter-spacing: -0.01em;
    }
    .topbar nav {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.35rem 1.1rem;
    }
    .topbar a {
      color: var(--muted);
      text-decoration: none;
      white-space: nowrap;
    }
    .topbar a:hover { color: var(--text); }
    .topbar .lang {
      color: var(--link);
      font-weight: 600;
    }
    .hero {
      padding: clamp(3.5rem, 12vw, 6.5rem) 0 clamp(3rem, 8vw, 4.5rem);
      text-align: center;
    }
    .hero h1 {
      font-size: clamp(2.5rem, 7vw, 3.75rem);
      font-weight: 600;
      letter-spacing: -0.022em;
      line-height: 1.05;
      margin: 0 0 0.35rem;
    }
    .hero .ver {
      display: inline-block;
      font-family: var(--mono);
      font-size: 11px;
      font-weight: 500;
      color: var(--muted);
      letter-spacing: 0.06em;
      margin-bottom: 1rem;
    }
    .hero .lead {
      font-size: clamp(1.05rem, 2.2vw, 1.25rem);
      color: var(--muted);
      max-width: 38rem;
      margin: 0 auto 2rem;
      font-weight: 400;
    }
    .quick {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 0.65rem;
      list-style: none;
      margin: 0;
      padding: 0;
    }
    .quick a {
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
    }
    .quick a:hover { opacity: 0.75; }
    .section {
      padding: clamp(3rem, 7vw, 5rem) 0;
      border-top: 1px solid var(--line);
    }
    .section-head {
      font-size: clamp(1.75rem, 4vw, 2.5rem);
      font-weight: 600;
      letter-spacing: -0.019em;
      line-height: 1.1;
      margin: 0 0 1rem;
    }
    .section-sub {
      font-size: 19px;
      color: var(--muted);
      max-width: 46rem;
      margin: 0 0 1.75rem;
    }
    .grid-2 {
      display: grid;
      grid-template-columns: 1fr;
      gap: clamp(1.5rem, 4vw, 2.5rem);
    }
    @media (min-width: 900px) {
      .grid-2 { grid-template-columns: 1fr 1fr; gap: 3rem 4rem; }
    }
    .card {
      background: var(--surface);
      border-radius: var(--radius);
      padding: clamp(1.5rem, 3vw, 2rem);
      border: 1px solid var(--line);
    }
    .card h3 {
      font-size: 14px;
      font-weight: 600;
      letter-spacing: 0.02em;
      text-transform: uppercase;
      color: var(--muted);
      margin: 0 0 0.75rem;
    }
    .card p, .card li {
      font-size: 15px;
      line-height: 1.5;
      color: var(--text);
    }
    .card p { margin: 0 0 0.85rem; }
    .card p:last-child { margin-bottom: 0; }
    .card ul {
      margin: 0;
      padding-left: 1.15rem;
      color: var(--muted);
    }
    .card ul li { margin-bottom: 0.4rem; }
    .price-row {
      font-size: clamp(1.75rem, 3.5vw, 2.25rem);
      font-weight: 600;
      letter-spacing: -0.02em;
      margin: 0 0 0.5rem;
    }
    .price-note {
      font-size: 15px;
      color: var(--muted);
      margin: 0;
    }
    code, .mono {
      font-family: var(--mono);
      font-size: 0.9em;
    }
    code {
      padding: 0.15em 0.4em;
      border-radius: 6px;
      background: var(--line);
    }
    table.legal {
      width: 100%;
      border-collapse: collapse;
      font-size: 15px;
    }
    table.legal th,
    table.legal td {
      text-align: left;
      vertical-align: top;
      padding: 0.85rem 0;
      border-bottom: 1px solid var(--line);
    }
    table.legal tr:last-child th,
    table.legal tr:last-child td { border-bottom: none; }
    table.legal th {
      width: min(12rem, 32%);
      color: var(--muted);
      font-weight: 500;
      padding-right: 1.25rem;
    }
    table.legal a { color: var(--link); text-decoration: none; }
    table.legal a:hover { text-decoration: underline; }
    .prose p {
      font-size: 15px;
      color: var(--muted);
      margin: 0 0 1rem;
      max-width: 52rem;
    }
    .prose p:last-child { margin-bottom: 0; }
    .prose strong { color: var(--text); font-weight: 600; }
    .prose a { color: var(--link); text-decoration: none; }
    .prose a:hover { text-decoration: underline; }
    .card.prose h3 {
      font-size: 17px;
      font-weight: 600;
      color: var(--text);
      text-transform: none;
      letter-spacing: -0.01em;
      margin: 0 0 0.65rem;
    }
    footer.site {
      padding: 2.5rem 0 4rem;
      border-top: 1px solid var(--line);
      font-size: 12px;
      color: var(--muted);
      text-align: center;
    }
"""


def _wrap(*, lang: str, title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="color-scheme" content="light dark" />
  <title>{title}</title>
  <style>
{LANDING_CSS}
  </style>
</head>
<body>
{body}
</body>
</html>"""


def html_landing_ja() -> str:
    sn, sv, ver = SERVICE_NAME, SERVICE_TAGLINE, APP_VERSION
    body = f"""
  <div class="topbar">
    <div class="shell inner">
      <a href="/" style="color:var(--text);font-weight:600;">{sn}</a>
      <nav aria-label="ページ内">
        <a href="#service">サービス</a>
        <a href="#pricing">料金</a>
        <a href="#payment">決済・返金</a>
        <a href="#legal">特商法</a>
        <a href="#terms">利用規約</a>
        <a href="#privacy">プライバシー</a>
        <a class="lang" href="/en">English</a>
      </nav>
    </div>
  </div>

  <header class="hero">
    <div class="shell">
      <h1>{sn}</h1>
      <div class="ver">v{ver}</div>
      <p class="lead">{sv}</p>
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
          <p><strong>適用</strong>：本規約は、{sn} ファクトチェック API（以下「本サービス」）の利用に適用されます。</p>
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
      <p>{sn} · Fact-check API · 本サイトは決済・事業者情報の公開用 URL として利用できます。</p>
    </div>
  </footer>
"""
    return _wrap(lang="ja", title=f"{sn} · Fact-check API", body=body)


def html_landing_en() -> str:
    sn, ver = SERVICE_NAME, APP_VERSION
    st_en = SERVICE_TAGLINE_EN
    body = f"""
  <div class="topbar">
    <div class="shell inner">
      <a href="/en" style="color:var(--text);font-weight:600;">{sn}</a>
      <nav aria-label="On this page">
        <a href="#service">Service</a>
        <a href="#pricing">Pricing</a>
        <a href="#payment">Payment &amp; refunds</a>
        <a href="#legal">Legal notice</a>
        <a href="#terms">Terms</a>
        <a href="#privacy">Privacy</a>
        <a class="lang" href="/">日本語</a>
      </nav>
    </div>
  </div>

  <header class="hero">
    <div class="shell">
      <h1>{sn}</h1>
      <div class="ver">v{ver}</div>
      <p class="lead">{st_en}</p>
      <ul class="quick" aria-label="Developer links">
        <li><a href="/docs">OpenAPI (Swagger)</a></li>
        <li><a href="/.well-known/agent-card.json">A2A agent-card</a></li>
        <li><a href="/.well-known/ai-agent.json">Legacy agent JSON</a></li>
        <li><a href="/health"><span class="mono">GET &#47;health</span></a></li>
      </ul>
    </div>
  </header>

  <main>
    <section id="service" class="section">
      <div class="shell">
        <h2 class="section-head">Service</h2>
        <p class="section-sub">
          <strong>Fact-checking (claim verification) over HTTP</strong> for software and AI agents.
          You send a claim as text; we analyze it using public web search and return a JSON response with a score, references, and a short summary.
        </p>
        <div class="grid-2">
          <div class="card">
            <h3>What you receive</h3>
            <p>Digital service (API only). Nothing is shipped physically. After payment succeeds, we return verification results for that request immediately.</p>
            <ul>
              <li>Primary endpoint: <code>POST /verify</code></li>
              <li>If unpaid: <code>402 Payment Required</code> and <code>X-Payment-Link</code> to Stripe Checkout</li>
              <li>Agent discovery: <code>/.well-known/agent-card.json</code></li>
            </ul>
          </div>
          <div class="card">
            <h3>Payments &amp; compliance</h3>
            <p>
              Card payments are processed by <strong>Stripe, Inc.</strong> via Checkout. Full card numbers are not stored on our servers; handling follows Stripe&rsquo;s policies.
            </p>
            <p style="margin-bottom:0;">
              The <strong>legal notice</strong> below (Japan Act on Specified Commercial Transactions) lists the seller name, address, contact, payment method, delivery timing, and return policy in Japanese as required domestically. An English summary of the same facts is included in the table labels where helpful.
            </p>
          </div>
        </div>
      </div>
    </section>

    <section id="pricing" class="section">
      <div class="shell">
        <h2 class="section-head">Pricing</h2>
        <p class="section-sub">
          Prices are shown in Japanese yen (JPY), tax included. Usage-based: one verification request equals one billable API call.
        </p>
        <div class="card" style="max-width: 36rem;">
          <p class="price-row">¥100 (tax included) per request</p>
          <p class="price-note">
            Included: one fact-check API use for that paid request.
            Your card issuer or network may charge fees under their own rules, in addition to our listed price.
          </p>
        </div>
      </div>
    </section>

    <section id="payment" class="section">
      <div class="shell">
        <h2 class="section-head">Payment, cancellation &amp; refunds</h2>
        <div class="grid-2">
          <div class="card prose">
            <h3>Payment</h3>
            <p>Credit and debit cards via Stripe Checkout. Follow the on-screen steps. When payment completes, API access is authorized for that purchase.</p>
          </div>
          <div class="card prose">
            <h3>Cancellations &amp; refunds</h3>
            <p>
              This is a digital service (API-delivered verification). <strong>After verification has completed and results have been delivered, we do not offer refunds or cancellations.</strong>
              Where Japanese law or other applicable law requires a refund, that obligation still applies.
            </p>
            <p>For duplicate charges, clear payment errors, or obvious system failures, contact us at the email below; we will review and respond in good faith.</p>
          </div>
        </div>
      </div>
    </section>

    <section id="legal" class="section">
      <div class="shell">
        <h2 class="section-head">Specified Commercial Transactions (Japan)</h2>
        <p class="section-sub">
          Legally required disclosure for online sales of digital services in Japan (Act on Specified Commercial Transactions). Values match the Japanese version on <a href="/">/</a>.
        </p>
        <div class="card">
          <table class="legal" aria-label="Specified commercial transactions disclosure">
            <tbody>
              <tr><th scope="row">Seller (operator)</th><td>林 連太郎 (Rentaro Hayashi)</td></tr>
              <tr><th scope="row">Address</th><td>〒849-0937 佐賀県佐賀市鍋島4丁目2-11 コーポ鍋島２０２, Japan</td></tr>
              <tr><th scope="row">Contact</th><td><a href="mailto:carai@cocarai.com">carai@cocarai.com</a> (email inquiries)</td></tr>
              <tr><th scope="row">Payment method</th><td>Credit card via Stripe</td></tr>
              <tr><th scope="row">Delivery</th><td>Immediately after payment (JSON API response)</td></tr>
              <tr><th scope="row">Returns</th><td>Digital content: no returns in principle (see Payment &amp; refunds above)</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section id="terms" class="section">
      <div class="shell">
        <h2 class="section-head">Terms of service (summary)</h2>
        <p class="section-sub">Please read before using the API. A separate full agreement may apply if we publish one later.</p>
        <div class="card prose">
          <p><strong>Scope</strong>: These terms govern use of the {sn} fact-checking API (&ldquo;Service&rdquo;).</p>
          <p><strong>Contract</strong>: When you call the API and payment via Stripe completes for a request, a contract is formed for that request.</p>
          <p><strong>Prohibited use</strong>: No illegal activity, infringement of third-party rights, unauthorized access, abusive load, fraud, or other use we reasonably deem inappropriate.</p>
          <p><strong>Disclaimer</strong>: Results are based on public information and are not guaranteed complete or error-free. Except where mandatory law says otherwise, we are not liable for indirect damages.</p>
          <p><strong>Law &amp; venue</strong>: Governed by the laws of Japan. Courts at the operator&rsquo;s location in Japan have exclusive jurisdiction unless prohibited by law.</p>
        </div>
      </div>
    </section>

    <section id="privacy" class="section">
      <div class="shell">
        <h2 class="section-head">Privacy (summary)</h2>
        <p class="section-sub">Key points about personal data. If we publish a full privacy policy, that document prevails.</p>
        <div class="card prose">
          <p><strong>Payments</strong>: Stripe collects and processes card data. We may receive limited billing metadata from Stripe as needed to operate payments.</p>
          <p><strong>Service operation</strong>: Claim text you send may be forwarded to search providers to perform verification. We may retain logs and billing records for a limited time for operations and accounting.</p>
          <p><strong>Support</strong>: If you email us, we use your message to respond and may retain it as correspondence.</p>
          <p><strong>Rights</strong>: For access, correction, or deletion requests under applicable privacy law, contact <a href="mailto:carai@cocarai.com">carai@cocarai.com</a>.</p>
        </div>
      </div>
    </section>
  </main>

  <footer class="site">
    <div class="shell">
      <p>{sn} · Fact-check API · This site may be used as the public business URL for payment and partner review.</p>
    </div>
  </footer>
"""
    return _wrap(lang="en", title=f"{sn} · Fact-check API", body=body)
