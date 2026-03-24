# VeriNode — 本番デプロイ

## 作業分担: Cursor／リポジトリで済むこと vs 代行不可

| 区分 | 内容 |
|------|------|
| **済（このリポジトリ）** | `POST /verify`、402 課金ゲート、Stripe Checkout、`/.well-known/agent-card.json` / `ai-agent.json`、ルート特商法 HTML、`registration/` + `print_a2a_registry_payload.py`、`webhooks`、`Dockerfile` / `render.yaml`、`pytest` など |
| **代行不可（当人必須）** | 各サービスへのログイン、**秘密の入力**、**Stripe 審査・銀行・本番有効化**、**DNS**、**レジストリへの API POST**、**法務判断**など。詳細チェックリストは [OPERATOR_ONLY.md](./OPERATOR_ONLY.md)。 |

ローカル用コマンド短縮: `make install` → `make test` → `make run`（課金試験は `make run-payment`）。

**作業を順番に進める**: [SETUP_STEPS.md](./SETUP_STEPS.md)。**Checkout・デプロイ・Webhook・Agentic Commerce を画面操作レベルで**は [GUIDE_CHECKOUT_DEPLOY_STRIPE.md](./GUIDE_CHECKOUT_DEPLOY_STRIPE.md)。**A2A レジストリ登録**は [A2A_REGISTRATION.md](./A2A_REGISTRATION.md)。**申請で Cursor が代行できない作業一覧**は [OPERATOR_ONLY.md](./OPERATOR_ONLY.md)。

## ロードマップ（最短ルート）

1. **キー取得**: Serper（または Google CSE）、Stripe（[ダッシュボード](https://dashboard.stripe.com) のテスト／本番シークレット）。
2. **ローカル確認**: `VERIFY_SKIP_PAYMENT=1` で `/verify` と `GET /.well-known/ai-agent.json` を確認。
3. **課金**: `VERIFY_SKIP_PAYMENT=0` と Stripe（`STRIPE_SECRET_KEY` + 公開オリジン。`PUBLIC_BASE_URL` のほか、Vercel / Render / Railway では `VERCEL_URL` / `RENDER_EXTERNAL_URL` / `RAILWAY_PUBLIC_DOMAIN` が自動利用される）。402 → `X-Payment-Link` → 支払後 `X-Payment-Proof: cs_...`。
4. **Webhook（任意）**: Stripe で `https://<公開URL>/webhooks/stripe` を登録し、`STRIPE_WEBHOOK_SECRET` を設定（将来のクレジット台帳用）。
5. **公開**: デプロイ後 URL をエージェントカード `/.well-known/ai-agent.json` と一緒に共有。Stripe Agentic Commerce 等へ登録する場合は同じベース URL を使う。
6. **MCP**: サーバーレスでは stdio MCP は動かない。常時起動環境で `python -m app.mcp_server`。

## 共通: 環境変数

Vercel の **Environment Variables** や各ホストのシークレット設定に、`.env.example` と同じ名前で値を登録する。  
本番では `VERCEL=1` が自動で付くため `.env` ファイルは読まれない（`app/config.py` の挙動）。

必須（どちらか一方）:

- `SERPER_API_KEY` **または** `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_CX`

課金ゲートを本番で有効にする場合（**どちらか**）:

- **Stripe（推奨）**: `VERIFY_SKIP_PAYMENT=0`、`STRIPE_SECRET_KEY`、および公開オリジン（**`PUBLIC_BASE_URL`** またはホスト既定の `VERCEL_URL` / `RENDER_EXTERNAL_URL` / `RAILWAY_PUBLIC_DOMAIN`）。任意で `STRIPE_PRICE_ID`（固定 Price）、`STRIPE_WEBHOOK_SECRET`（Webhook 用）。
- **固定トークン**: `VERIFY_PAYMENT_TOKEN`、`PAYMENT_LINK_URL`（402 時の誘導先）。

## エージェント発見

- `GET /.well-known/agent-card.json` — [Google A2A](https://github.com/google/A2A) の Well-Known Agent Card（camelCase）。レジストリ登録手順は [A2A_REGISTRATION.md](./A2A_REGISTRATION.md)。
- `GET /.well-known/ai-agent.json` — VeriNode 従来の記述（課金・OpenAPI リンクなど）。

## Vercel

1. [Vercel](https://vercel.com) にリポジトリを接続する。
2. **Root Directory** はこのプロジェクトのルート（`server.py` がある階層）。
3. ダッシュボードで上記の環境変数を **Production**（必要なら Preview）に設定する。
4. デプロイ後、`https://<project>.vercel.app/health` で疎通確認する。

CLI の例（要 [Vercel CLI](https://vercel.com/docs/cli) 48.1.8+）:

```bash
npm i -g vercel
vercel
```

制約: アプリは **単一の Vercel Function** として動く。実行時間・ペイロード上限は [Functions の制限](https://vercel.com/docs/functions/limitations) に従う。  
**MCP（stdio）** はサーバーレスでは動かないため、エージェント用 MCP はローカルまたは常時起動の VPS で `python -m app.mcp_server` を使う。

## Docker（Railway / Render / Fly.io / Google Cloud Run など）

```bash
docker build -t verify-api .
docker run --rm -p 8000:8000 \
  -e SERPER_API_KEY="..." \
  -e VERIFY_SKIP_PAYMENT=1 \
  verify-api
```

ホストが `PORT` を渡す場合、Dockerfile の `CMD` がそれを使う。

### Render

`render.yaml` をリポジトリに含めている場合、Render ダッシュボードから Blueprint として接続できる。`sync: false` の変数は UI で手入力する。

### Railway

Dockerfile を検出して自動ビルドされることが多い。環境変数は Project → Variables に設定する。

## 本番の健全性チェック

- `GET /health` → `{"ok": true}`
- `GET /.well-known/agent-card.json` → A2A Well-Known Agent Card
- `GET /.well-known/ai-agent.json` → VeriNode 従来の JSON
- `POST /verify` に `{"claim":"..."}`（検索 API キーが有効なこと）
- 課金ありの場合: 証明なしで `402` と `X-Payment-Link`（Stripe なら Checkout URL）、支払済み `cs_...` を `X-Payment-Proof` に付けて `200`
- `POST /billing/checkout-session` → `url` と `checkout_session_id`（課金フローを 402 なしで開始したい場合）

## 代行不可タスクのチェックリスト（順に実施）

1. [Serper.dev](https://serper.dev)（または Google CSE）でキー取得 → `.env` またはホストの Variables に設定。
2. [Stripe Dashboard](https://dashboard.stripe.com) で **Secret key**（テスト／本番）取得 → 同上。任意で Product/Price → `STRIPE_PRICE_ID`。
3. 課金テスト: ブラウザで Checkout を開き **4242…** で支払い → `cs_test_...` を `X-Payment-Proof` に付与して API を再呼び出し。
4. 本番 URL が決まったら Stripe で Webhook `https://<ドメイン>/webhooks/stripe` を登録 → **Signing secret** を `STRIPE_WEBHOOK_SECRET` に設定。
5. Vercel / Render / Railway 等で **デプロイ**し、`.env.example` と同じ名前で **本番用環境変数**を入力（`VERIFY_SKIP_PAYMENT=0` を本番で使うかは方針次第）。
6. 必要なら **Stripe Agentic Commerce** 等に **公開ベース URL** を登録（最新の登録要件は Stripe 公式を確認）。
7. 有料提供するなら **利用規約・返金・問い合わせ**など、管轄に応じた表示を用意する。

**ローカル検証**:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env   # SERPER_API_KEY 等を記入
pytest
uvicorn app.main:app --reload --port 8000
```

## Step 4 — 課金ゲート（402）をローカルで試す

**Cursor / リポジトリ側（済）**: `scripts/run_with_payment_gate.sh`、Stripe 経路の単体テスト `tests/test_payment_stripe_402.py`。

**あなたが行うこと**:

1. `.env` に **Stripe テスト用** `STRIPE_SECRET_KEY=sk_test_...` が入っていることを確認する（本番の `sk_live_` はローカル検証に使わない）。**Stripe を使うなら `VERIFY_PAYMENT_TOKEN` は空**（サンプルの `your-shared-secret` を残すと `example.com` のリンク側に行く）。
2. **ローカルでは** `PUBLIC_BASE_URL=http://127.0.0.1:（uvicorn のポート）` を必ず入れる。キーだけで URL が無い場合は **503**（`stripe_needs_public_base_url`）となり、誤誘導を防ぐ。
3. 課金ありで起動する: `./scripts/run_with_payment_gate.sh`（既定ポート 8000）。別ポートなら `PORT=8765 ./scripts/run_with_payment_gate.sh`（このとき `PUBLIC_BASE_URL` は自動で `http://127.0.0.1:8765` になる）。
4. 別ターミナルで `POST /verify`（証明なし）→ **402** とヘッダー **`X-Payment-Link`**（`checkout.stripe.com`）を確認。ブラウザでその URL を開き、テストカード **4242424242424242** で支払う。
5. 支払い完了後、Stripe の成功画面または API 応答で **`cs_test_...`**（Checkout Session ID）を控え、`X-Payment-Proof: cs_test_...` を付けて `POST /verify` を再実行する → **200** と検証 JSON が返る。
6. （任意）Webhook を試す: [Stripe CLI](https://stripe.com/docs/stripe-cli) をインストールし、`stripe listen --forward-to localhost:8000/webhooks/stripe` を実行。ダッシュボードで得たシークレットを `.env` の `STRIPE_WEBHOOK_SECRET` に設定してからイベントを流す。

**ローカル検証後**: 通常開発に戻すには `.env` の `VERIFY_SKIP_PAYMENT=1` に戻す。

**自動テスト（ネットワーク不要）**:

```bash
pytest tests/test_payment_stripe_402.py -v
```
