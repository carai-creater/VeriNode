# VeriNode — 手順を一つずつ進める

各ステップのうち、**あなたがブラウザや各サービスで行う部分**と、**ターミナルでコマンドする部分**を分けて書いています。  
**Checkout → デプロイ → Webhook → Agentic Commerce** をさらに細かくやる場合は [GUIDE_CHECKOUT_DEPLOY_STRIPE.md](./GUIDE_CHECKOUT_DEPLOY_STRIPE.md)。  
秘密情報（API キーなど）は **Git にコミットしない**でください。

---

## Step 0 — リポジトリと Python

**あなたが行うこと**

1. このプロジェクトフォルダを開く（Cursor でそのまま作業でよい）。
2. ターミナルでプロジェクトルートに移動する。

**コマンド（コピー可）**

```bash
cd /path/to/VeriNode
make install
make test
```

`6 passed` 程度が出れば環境は足りています。

---

## Step 1 — 検索 API（Serper）

**あなたが行うこと**

1. [Serper.dev](https://serper.dev) にログインし、API キーを発行する。
2. プロジェクトの **`.env`** を開き、`SERPER_API_KEY=` の右にキーを貼る（引用符は不要）。
3. Google CSE を使う場合は Serper の代わりに `GOOGLE_CSE_API_KEY` と `GOOGLE_CSE_CX` を埋める（どちらか一方でよい）。

**確認コマンド**

```bash
make run
```

別ターミナルで:

```bash
curl -sS http://127.0.0.1:8000/health
curl -sS -X POST http://127.0.0.1:8000/verify \
  -H 'Content-Type: application/json' \
  -d '{"claim":"テスト用の主張"}'
```

`503` と検索未設定が出る場合は `.env` の読み込みかキー名を確認する。成功時は JSON で `status` / `sources` などが返る。

---

## Step 2 — エージェントカード（公開メタデータ）

**コード側**: 実装済み（追加作業なし）。

**あなたが行うこと**

1. サーバー起動中にブラウザまたは curl で開く:  
   `http://127.0.0.1:8000/.well-known/ai-agent.json`
2. JSON に `name`, `api`, `auth` が含まれることを確認する。

---

## Step 3 — Stripe（テストモード）

**あなたが行うこと**

1. [Stripe Dashboard](https://dashboard.stripe.com) にログインし、**テストモード**にする。
2. **Developers → API keys** で Secret key（`sk_test_...`）をコピーする。
3. `.env` の `STRIPE_SECRET_KEY=` に貼る。
4. **Stripe Checkout を使う**なら `.env` の **`VERIFY_PAYMENT_TOKEN` は空**にする（値があると `example.com` 方式に寄る）。
5. ローカルでは **`PUBLIC_BASE_URL=http://127.0.0.1:8000`**（ポートは `uvicorn` と同じ）を必ず設定する。

**コード側**: `STRIPE_SECRET_KEY` だけあって `PUBLIC_BASE_URL` が無いと **503**（`stripe_needs_public_base_url`）になる（誤誘導防止）。

---

## Step 4 — 課金ゲート（HTTP 402）

**あなたが行うこと**

1. `.env` で **`VERIFY_SKIP_PAYMENT=0`** にする（試験後は `1` に戻すと課金なしで開発しやすい）。
2. 起動:

```bash
make run-payment
```

（または `./scripts/run_with_payment_gate.sh`）

3. 別ターミナル:

```bash
curl -i -X POST http://127.0.0.1:8000/verify \
  -H 'Content-Type: application/json' \
  -d '{"claim":"テスト"}'
```

4. **`HTTP/1.1 402`** と **`X-Payment-Link: https://checkout.stripe.com/...`** を確認する。
5. **ブラウザ**でその URL を開き、テストカード **4242 4242 4242 4242**（有効期限・CVCは適当で可）で支払う。
6. 成功後に表示される **`cs_test_...`** をコピーする。
7. 再リクエスト:

```bash
curl -sS -X POST http://127.0.0.1:8000/verify \
  -H 'Content-Type: application/json' \
  -H 'X-Payment-Proof: cs_test_ここに貼る' \
  -d '{"claim":"テスト"}'
```

**200** と検証結果が返れば Step 4 完了。

**任意（別オリジンのフロントから fetch する場合）**

- `.env` に `CORS_ALLOW_ORIGINS=http://localhost:3000` のようにカンマ区切りで許可オリジンを書く（402 の `X-Payment-Link` を JavaScript で読むのに `expose_headers` が有効になる）。

---

## Step 5 — Webhook（任意）

**あなたが行うこと**

1. [Stripe CLI](https://stripe.com/docs/stripe-cli) をインストールする。
2. ローカルで:

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

3. 表示された **Signing secret**（`whsec_...`）を `.env` の `STRIPE_WEBHOOK_SECRET` に入れる。
4. サーバー再起動後、Stripe からイベントが届くと `POST /webhooks/stripe` が **200** で `received` を返す。

**本番**: Stripe ダッシュボードでエンドポイント URL を `https://あなたのドメイン/webhooks/stripe` に登録し、本番用 Signing secret をホストの環境変数に設定する。

---

## Step 6 — 本番デプロイ

**あなたが行うこと**

1. Vercel / Render / Railway 等で **リポジトリを接続**し、**ビルド・デプロイ**する。
2. ホストの **Environment Variables** に、`.env.example` と同じ名前で本番用の値を入れる（秘密はダッシュボードのみ）。
3. `VERIFY_SKIP_PAYMENT` を本番で `0` にするかは運用方針で決める。
4. `GET https://あなたのURL/health` と `POST /verify`、必要なら 402 フローを再度確認する。

詳細は [DEPLOY.md](./DEPLOY.md)。

---

## Step 7 — エージェント市場・登録（任意）

**あなたが行うこと**

1. [Stripe Agentic Commerce](https://stripe.com) 等、利用するプログラムの **最新の登録手順**を読む。
2. 公開 URL（HTTPS）と `/.well-known/ai-agent.json` の内容が要件に合うか確認し、申請・登録する。

**コード側**: Agent Card の JSON 構造は `app/agent_card.py` で生成される。要件変更があればそこを直す。

---

## 困ったとき

| 現象 | 確認すること |
|------|----------------|
| 402 なのに `example.com` のリンク | `VERIFY_PAYMENT_TOKEN` を空にしたか、`STRIPE_SECRET_KEY` + `PUBLIC_BASE_URL` があるか |
| 503 `stripe_needs_public_base_url` | ローカルなら `PUBLIC_BASE_URL=http://127.0.0.1:ポート` |
| 検索 503 | `SERPER_API_KEY` または Google CSE の両方 |
| pytest が変 | テストは `.env` を読まない（`tests/conftest.py`）。本番用キーはテストに影響しない |
