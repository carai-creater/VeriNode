# A2A（Agent-to-Agent）登録ガイド

**申請で「当人だけがやること」全体**は [OPERATOR_ONLY.md](./OPERATOR_ONLY.md)。ここは A2A 周辺に絞った説明です。

VeriNode は **Google A2A 仕様の Well-Known URL** で Agent Card を公開します。  
レジストリへの **登録操作自体**は、あなたが各サービスの画面または API で行います（Cursor からは代行できません）。

**登録用 JSON の生成（ローカル）:**

```bash
PUBLIC_BASE_URL=https://あなたの本番ドメイン python3 scripts/print_a2a_registry_payload.py
```

## 1. 公式の位置づけ

| リソース | URL |
|----------|-----|
| Google A2A 仕様（Agent Discovery） | [A2A Specification](https://github.com/google/A2A)（Well-Known: `/.well-known/agent-card.json`） |
| コミュニティ A2A Registry（任意） | [a2a-registry.dev](https://a2a-registry.dev/) · API: [api.a2a-registry.dev](https://api.a2a-registry.dev/) |
| Google Cloud Marketplace の Agent Card（別プログラム） | [Cloud Marketplace — Agent Card](https://cloud.google.com/marketplace/docs/partners/ai-agents/agent-card) |

## 2. 本番でまず確認すること

HTTPS のベース URL を `BASE` とします（例: `https://verinode.onrender.com`）。

```bash
curl -sS "$BASE/.well-known/agent-card.json" | head -c 400
```

JSON に `name`, `supportedInterfaces`, `skills` が含まれていれば discovery 用エンドポイントは動作しています。

**注意**: VeriNode は **A2A コアの `SendMessage` / Task API** は実装していません。`POST /verify` という **独自 REST** と **HTTP 402 + Stripe** を Agent Card の `skills` と `metadata` に明示しています。フル A2A クライアントがそのまま動くとは限りません。

## 3. A2A Registry（api.a2a-registry.dev）への登録例

[クイックスタートの例](https://a2a-registry.dev/) に合わせ、**レジストリが求める snake_case** の `agent_card` で登録します。  
`url` は **あなたの本番オリジン**に置き換えてください。

`preferred_transport` はレジストリの例では `JSONRPC` ですが、本サービスは **REST の /verify** です。登録が拒否される場合はレジストリのドキュメントに従い、`metadata` に実際の呼び出し方法を書くか、対応トランスポートを確認してください。

### JSON-RPC（推奨とされる経路）

```bash
curl -X POST "https://api.a2a-registry.dev/jsonrpc" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "register_agent",
    "params": {
      "agent_card": {
        "name": "verinode",
        "description": "AI エージェント向けファクトチェック API（HTTP POST /verify、402+Stripe）",
        "url": "https://あなたのドメイン",
        "version": "0.2.0",
        "protocol_version": "0.3.0",
        "preferred_transport": "JSONRPC",
        "skills": [
          {
            "id": "verinode-verify",
            "description": "POST /verify JSON {\"claim\":\"...\"}; 402時は X-Payment-Link で Stripe 後 X-Payment-Proof に cs_..."
          }
        ]
      }
    },
    "id": 1
  }'
```

### REST 代替

```bash
curl -X POST "https://api.a2a-registry.dev/agents" \
  -H "Content-Type: application/json" \
  -d '{"agent_card": { ... 上と同じ ... }}'
```

成功・失敗のメッセージはレスポンス本文を確認してください。**API の利用規約・認証**があれば [公式ドキュメント](https://a2a-registry.dev/documentation/) に従います。

## 4. Google Cloud / Stripe など別プロダクト

- **Marketplace パートナー**向け Agent Card は提出形式が異なる場合があります。上記 Cloud ドキュメントを参照してください。  
- **Stripe Agentic Commerce** は別仕様です。[Agentic commerce ドキュメント](https://docs.stripe.com/agentic-commerce) を参照してください。

## 5. このリポジトリで公開している URL

| パス | 内容 |
|------|------|
| `/.well-known/agent-card.json` | Google A2A 風 Agent Card（camelCase、HTTP+JSON を宣言） |
| `/.well-known/ai-agent.json` | VeriNode 従来の記述（課金・OpenAPI リンクなど） |

課金ミドルウェア有効時も、上記 `/.well-known/*` は **402 対象外**です。
