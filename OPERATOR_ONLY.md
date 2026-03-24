# 申請まわり — Cursor でできないこと（当人がやること）

リポジトリ側では **Well-Known・特商法 HTML・ペイロード生成スクリプト**まで用意済みです。  
以下は **ログイン・入力・送金・法的判断**が必要なため、**あなたがブラウザや各ダッシュボードで実施**してください。

---

## すでにリポジトリ／Cursor で用意されているもの

- `GET /` … 特商法表記付き HTML（Stripe 審査用サイト URL に使える）
- `GET /.well-known/agent-card.json` … [Google A2A](https://github.com/google/A2A) 風 Agent Card
- `GET /.well-known/ai-agent.json` … VeriNode 従来の記述
- `registration/a2a-registry.agent_card.json` + `scripts/print_a2a_registry_payload.py` … レジストリ申請用 JSON の生成
- 手順の詳細 … [A2A_REGISTRATION.md](./A2A_REGISTRATION.md)、[GUIDE_CHECKOUT_DEPLOY_STRIPE.md](./GUIDE_CHECKOUT_DEPLOY_STRIPE.md)、[DEPLOY.md](./DEPLOY.md)

---

## 1. 本番 URL・HTTPS（インフラ）

1. **Render / Vercel / Railway 等**にログインし、サービスが **HTTPS** で公開されていることを確認する。
2. **環境変数**に、`.env.example` と同じ名前で **本番用の値**を入力する（`SERPER_API_KEY`、`STRIPE_SECRET_KEY`、`PUBLIC_BASE_URL`、`VERIFY_SKIP_PAYMENT` など）。  
   - **秘密は Git に入れない**（ホストの Variables のみ）。
3. カスタムドメインを使う場合は **DNS** をドメイン管理画面で設定する。

**確認コマンド（ローカル）:**

```bash
curl -sS -o /dev/null -w "%{http_code}\n" "https://あなたのドメイン/health"
curl -sS "https://あなたのドメイン/.well-known/agent-card.json" | head -c 200
```

---

## 2. Stripe（本番審査・有効化）

1. [Stripe Dashboard](https://dashboard.stripe.com) にログインする。
2. **事業者情報・本人確認・銀行口座**など、ダッシュボードが求める項目を **画面の指示どおり**に提出する。
3. **ウェブサイト URL** には、特商法が載っている **本番のルート**（例: `https://verinode.onrender.com/`）を登録する。
4. **本番モード**で利用する場合は **制限キー（`sk_live_...`）** を取得し、ホストの環境変数に設定する（テストキーのままにしない）。
5. **Webhook** を使う場合: エンドポイント `https://ドメイン/webhooks/stripe` をダッシュボードで登録し、**Signing secret** を `STRIPE_WEBHOOK_SECRET` に設定する。
6. 返品不可・デジタル商品など、**Stripe が求める説明**がサイト（`/` の HTML）と矛盾していないか自分で確認する。

※ 審査結果や追加資料の要請は **Stripe からのメール／ダッシュボード**に従う。

---

## 3. A2A Registry（任意・外部サービス）

1. 本番の **`PUBLIC_BASE_URL`**（`https://...`、末尾スラッシュなし）を決める。
2. ターミナルでペイロードを生成する:

```bash
cd /path/to/VeriNode
PUBLIC_BASE_URL=https://あなたのドメイン python3 scripts/print_a2a_registry_payload.py
```

3. 表示された JSON を確認し、[A2A Registry API](https://api.a2a-registry.dev/) に **自分で POST** する（例は [A2A_REGISTRATION.md](./A2A_REGISTRATION.md)）。
4. レジストリ側で **アカウント・API キー・利用規約**が必要なら、そちらに従う。

※ `preferred_transport` と実装（REST）の差異で弾かれる場合は、**レジストリのドキュメント**またはサポートに確認する。

---

## 4. Google Cloud Marketplace / Stripe Agentic Commerce など

- **別プログラム**ごとに提出物が異なります。  
- [Cloud — Agent Card](https://cloud.google.com/marketplace/docs/partners/ai-agents/agent-card)、[Stripe Agentic Commerce](https://docs.stripe.com/agentic-commerce) など **最新の公式手順**に従い、**ポータルから申請**する。

---

## 5. 法務・表記（判断は当人）

- 特商法・プライバシー・特定電子メール法など、**管轄と事業形態**に応じた表記が追加で必要かは **専門家または自治体・Stripe の案内**で判断する。
- 連絡先メール・所在地の変更があれば **`app/main.py` の HTML** を直し、再デプロイする（コード変更は Cursor で可能）。

---

## チェックリスト（コピー用）

- [ ] 本番 `https://.../health` と `/.well-known/agent-card.json` が取れる  
- [ ] ホストに **本番用環境変数**を設定した（秘密はリポジトリに無い）  
- [ ] Stripe に **サイト URL** を登録し、**本番キー / Webhook** を必要に応じ設定した  
- [ ] A2A Registry を使うなら **`print_a2a_registry_payload.py` → curl** を自分で実行した  
- [ ] その他のプログラム（GCP / Agentic Commerce）は **公式の申請画面**を完了した  
