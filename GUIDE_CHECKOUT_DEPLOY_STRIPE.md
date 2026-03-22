# 手元で一つずつ：Checkout → デプロイ → Webhook / Agentic Commerce

このファイルは **あなたがブラウザ・各サービスで行う操作**だけを、番号順に書いています。  
秘密情報は **コピペしてもチャットや Git に貼らない**でください。

---

## パート 1 — ブラウザで Checkout し、`cs_test_...` を手に入れる

### 1-0. 事前確認（`.env`）

次を満たしていること（値はここに書かない）。

1. `VERIFY_SKIP_PAYMENT=0`
2. `STRIPE_SECRET_KEY` が **`sk_test_` で始まる**テスト用シークレットキー
3. `VERIFY_PAYMENT_TOKEN` が **空**（Stripe モードにしたいとき）
4. `PUBLIC_BASE_URL` が **今から起動するサーバーと同じオリジン**（例: `http://127.0.0.1:8000`）

### 1-1. API を起動

ターミナル（プロジェクトルート）:

```bash
./scripts/run_with_payment_gate.sh
```

別ポートにしたい場合:

```bash
PORT=8765 ./scripts/run_with_payment_gate.sh
```

（このとき `PUBLIC_BASE_URL` はスクリプトが `http://127.0.0.1:8765` に合わせます。自分で `.env` に固定している場合は **ポートを一致**させる。）

### 1-2. 支払いリンクを取る

**別のターミナル**で:

```bash
curl -i -X POST "http://127.0.0.1:8000/verify" \
  -H "Content-Type: application/json" \
  -d '{"claim":"Checkout テスト"}'
```

確認すること:

- 1 行目付近が **`HTTP/1.1 402`**
- ヘッダーに **`x-payment-link: https://checkout.stripe.com/...`**（または類似の Stripe ドメイン）

`example.com` だけのリンクのときは、まだ **トークン方式**になっているか **`PUBLIC_BASE_URL` / Stripe キー**が足りない。[SETUP_STEPS.md](./SETUP_STEPS.md) の「困ったとき」表を見る。

### 1-3. ブラウザで支払う

1. ターミナルに出た **`x-payment-link` の URL 全文**をコピーする。
2. ブラウザのアドレスバーに貼り付けて Enter。
3. Stripe の Checkout 画面が開く。
4. **メールアドレス**はテストなので任意の形式でよい（例: `test@example.com`）。
5. カード番号に **`4242 4242 4242 4242`** を入れる。
6. 有効期限は **未来の月/年**（例: 12 / 34）。
7. CVC は **任意の 3 桁**（例: `123`）。
8. 氏名・郵便番号を求められたら適当に埋めて **支払う / Pay** を押す。

### 1-4. `cs_test_...` をコピーする（2 通りのどちらかでよい）

**方法 A（おすすめ）: 成功後のページ（このプロジェクト）**

支払い成功後、ブラウザは次のような URL に飛びます（`PUBLIC_BASE_URL` がそのまま使われます）。

```text
http://127.0.0.1:8000/billing/success?session_id=cs_test_XXXXX
```

1. アドレスバーの **`session_id=` の後ろ**から **`cs_test_` で始まる部分だけ**をコピーする（`&` が無ければ URL 末尾まで）。
2. ページ本文に JSON が出ていれば、フィールド **`checkout_session_id`** に同じ値が載っているので、そこからコピーしてもよい。

**方法 B: 402 の JSON（最初の curl）**

最初の `curl` のレスポンス body に、次のフィールドがある場合があります。

- **`checkout_session_id`**: その値がそのまま `cs_test_...` です。ブラウザに行かずに API 連携だけ試すときに使えます。

### 1-5. 支払い済みとして API を再呼び出し

```bash
curl -sS -X POST "http://127.0.0.1:8000/verify" \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: ここにcs_test_を貼る" \
  -d '{"claim":"Checkout テスト"}'
```

- **`200`** と JSON（`status`, `score`, `sources` など）が返れば、このパートは完了。
- まだ **402** のときは、`cs_test_` が丸ごとコピーできているか、**同じ Stripe モード（テスト）**のセッションか確認する。

### 1-6. 元に戻す（日常開発）

`.env` の **`VERIFY_SKIP_PAYMENT=1`** に戻すと、課金なしで `/verify` を叩ける。

---

## パート 2 — ホストにデプロイする（環境変数・DNS）

ここでは **Render** を例にします（リポジトリに `render.yaml` があるため）。Vercel / Railway も概要だけ後述します。

### 2-1. ソースをホストが読める場所に置く

1. **GitHub**（または GitLab 等）にリポジトリを push する。  
2. まだの場合は [GitHub の手順](https://docs.github.com/repositories/creating-and-managing-repositories/creating-a-new-repository) に従う。

### 2-2. Render で Web サービスを作る

1. [Render](https://render.com) にログインする。
2. **Dashboard → New → Blueprint**（または **Web Service** で Docker を選ぶ）。
3. リポジトリを接続し、このプロジェクトの **`render.yaml`** を使うか、**Dockerfile** デプロイを選ぶ。
4. デプロイが終わるまで待つ。
5. 画面上に出る **HTTPS の URL**（例: `https://verify-api-xxxx.onrender.com`）をメモする。これが **本番のベース URL**。

### 2-3. Render で環境変数を入れる

**Dashboard → 該当サービス → Environment**

次を **名前どおり**設定する（値はあなたの本番用・テスト用の方針で。ここに具体値は書かない）。

| 変数名 | 説明 |
|--------|------|
| `SERPER_API_KEY` | 検索用（または Google CSE 用のキー2つ） |
| `VERIFY_SKIP_PAYMENT` | 本番で課金するなら `0`、まず動作確認だけなら `1` |
| `STRIPE_SECRET_KEY` | テストなら `sk_test_...`、本番決済なら `sk_live_...` |
| `PUBLIC_BASE_URL` | **デプロイ後の HTTPS URL**（末尾スラッシュなし）。`https://verify-api-xxxx.onrender.com` のように **実際のドメイン** |
| `STRIPE_WEBHOOK_SECRET` | Webhook を使うときだけ（パート 3 のあとで `whsec_...` を入れる） |
| `STRIPE_PRICE_ID` | 固定 Price を使う場合のみ |
| `CORS_ALLOW_ORIGINS` | フロントを別ドメインに置く場合、カンマ区切りで許可オリジン |

**重要**: デプロイ後に URL が変わったら、**`PUBLIC_BASE_URL` を必ずその URL に合わせる**。Stripe Checkout の「戻り先」に使われます。

保存後、サービスが **再デプロイ**されるまで待つ。

### 2-4. 疎通確認（本番 URL に置き換える）

```bash
curl -sS "https://あなたのRenderのURL/health"
```

`{"ok":true}` が返れば HTTP は通っている。

```bash
curl -sS "https://あなたのRenderのURL/.well-known/ai-agent.json" | head -c 400
```

JSON が返れば Agent Card も公開されている。

### 2-5. 独自ドメインと DNS（任意）

1. Render の **Settings → Custom Domain** でドメインを追加する。
2. 表示される **CNAME / A レコード**を、ドメインを買っている会社（お名前.com、Cloudflare、Route53 など）の **DNS 管理画面**に **1 件ずつ**追加する。
3. Render が **証明書（HTTPS）を発行**するまで数分〜数十分待つ。
4. ドメインが有効になったら、**`PUBLIC_BASE_URL` をその `https://api.あなたのドメイン` に更新**して再デプロイする。

### 2-6. 他ホストのメモ

- **Vercel**: リポジトリ接続 → Root に `server.py` があるこのプロジェクトを選ぶ → Environment Variables に同じ名前で設定。`VERCEL_URL` が自動で付くため `PUBLIC_BASE_URL` は省略できることが多い（カスタムドメインで迷うなら明示でもよい）。  
- **Railway**: プロジェクト作成 → GitHub 接続 → Variables に同上。`RAILWAY_PUBLIC_DOMAIN` が使われるため `PUBLIC_BASE_URL` は省略できることがある。

詳細は [DEPLOY.md](./DEPLOY.md)。

---

## パート 3 — Stripe Webhook を登録する

### 3-1. 本番 URL が決まっていること

Webhook の URL は次の形です（ドメインはあなちのものに置き換え）。

```text
https://あなたの公開ドメイン/webhooks/stripe
```

ローカルだけで試す場合は **パート 3-5（Stripe CLI）**へ。

### 3-2. Stripe ダッシュボードでエンドポイントを追加

1. [Stripe Dashboard](https://dashboard.stripe.com) にログインする。
2. 右上で **テストモード / 本番モード**を、Webhook と合わせる（まずはテスト推奨）。
3. **Developers → Webhooks → Add endpoint**。
4. **Endpoint URL** に `https://あなたのドメイン/webhooks/stripe` を入力する。
5. **イベントを選択**する。最低限よく使うのは **`checkout.session.completed`**（必要に応じて他も追加）。
6. **Add endpoint** を確定する。

### 3-3. Signing secret をコピーする

1. いま作ったエンドポイントをクリックする。
2. **Signing secret** の **Reveal** を押し、**`whsec_...`** で始まる値をコピーする。
3. **Render（または Vercel / Railway）の Environment Variables** に  
   **`STRIPE_WEBHOOK_SECRET`** という名前で貼り付ける。
4. サービスを **再デプロイ**する（環境変数変更が反映されるまで待つ）。

### 3-4. 動作確認（本番）

1. Stripe の Webhook 画面で **Send test webhook** などでテストイベントを送る（UI があれば）。
2. または実際に **Checkout でテスト決済**を 1 回行い、**Webhook のログ**に **200** が残るか見る。

このアプリは成功時 **`{"received":true,"type":"...","id":"..."}`** を返します（`app/routers/webhooks.py`）。

### 3-5. ローカルだけで試す（Stripe CLI）

1. [Stripe CLI をインストール](https://stripe.com/docs/stripe-cli)する。
2. `stripe login` でブラウザ認証する。
3. ローカルで API を `8000` で動かしている状態で:

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

4. ターミナルに表示される **`whsec_...`** を `.env` の **`STRIPE_WEBHOOK_SECRET`** に入れる。
5. API を再起動する。
6. 別ターミナルで `stripe trigger checkout.session.completed` などを実行し、API 側のログで受け取りを確認する。

---

## パート 4 — Agentic Commerce（ダッシュボード・公式手順）

VeriNode は **`POST /verify` と HTTP 402 + Stripe Checkout** という独自形です。Stripe の **Agentic Commerce Protocol（ACP）** が求めるエンドポイント（Checkout の作成・更新・完了・キャンセル等）とは **完全一致しない**場合があります。**申請・登録前に必ず最新の公式ドキュメントで要件を確認**してください。

### 4-1. まず読む公式ドキュメント

- 概要: [Agentic commerce](https://docs.stripe.com/agentic-commerce)  
- プロトコル: [Integrate the Agentic Commerce Protocol](https://docs.stripe.com/agentic-commerce/protocol)  
- 仕様: [ACP specification](https://docs.stripe.com/agentic-commerce/protocol/specification)

### 4-2. あなたが用意する情報（一般的に必要になりやすいもの）

1. **公開 HTTPS のベース URL**（例: `https://api.example.com`）  
2. **エージェントの能力説明**として、次にアクセスできることの説明:  
   - `GET /.well-known/ai-agent.json`  
   - `POST /verify`（402 と `X-Payment-Link` の流れ）  
3. Stripe 側の **ダッシュボード**で、該当プログラムや Connect の設定があれば、**画面の指示どおり**に URL やコールバックを登録する。

### 4-3. プログラム参加・営業窓口

ドキュメントやダッシュボードに **Waitlist / Contact sales** がある場合は、そこから **Stripe 側の案内に従う**（URL は Stripe が更新することがあるため、ここでは固定リンクを強調しない）。

### 4-4. 技術的なギャップを埋める必要が出たら

ACP が求める REST 形と VeriNode が違う場合は、**別途 ACP 用の薄いアダプタ API** を立てるか、`/verify` を拡張する、といった **コード変更**が必要になることがあります。そのときは要件に合わせて別タスクとして相談する。

---

## チェックリスト（最後に一通り）

- [ ] ブラウザで Checkout 完了し **`cs_test_...`** を `X-Payment-Proof` で **`/verify` が 200** になる  
- [ ] 本番 URL で **`/health`** と **`/.well-known/ai-agent.json`** が取れる  
- [ ] **`PUBLIC_BASE_URL`** が本番の **https のオリジン**と一致している  
- [ ] Webhook URL を Stripe に登録し **`STRIPE_WEBHOOK_SECRET`** をホストに設定した  
- [ ] Agentic Commerce は **公式ドキュメント**で要件確認し、必要な登録だけ行った  
