# registration/

申請・外部レジストリ向けの **テンプレート**置き場です。

| ファイル | 用途 |
|----------|------|
| `a2a-registry.agent_card.json` | [A2A Registry](https://a2a-registry.dev/) 用 `agent_card` の雛形（`__PUBLIC_BASE_URL__` はスクリプトで置換） |

実際の JSON-RPC ボディの生成はリポジトリルートで:

```bash
PUBLIC_BASE_URL=https://あなたの本番ドメイン python3 scripts/print_a2a_registry_payload.py
```

当人がやる手順の一覧は [OPERATOR_ONLY.md](../OPERATOR_ONLY.md)。
