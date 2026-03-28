# VeriNode — 公式ランディング（Next.js）

FastAPI バックエンドとは別に動かす、App Router + Tailwind のマーケサイトです。

## 開発

```bash
cd web
npm install
npm run dev
```

ブラウザで [http://localhost:3000](http://localhost:3000) を開きます。

## 環境変数

`.env.local` に `web/.env.example` を参考に設定してください。`NEXT_PUBLIC_API_BASE_URL` に本番 API のオリジンを入れると、トップの cURL 例と「API 利用を始める」リンクがそのホストを指します。

## ページ

| パス | 内容 |
|------|------|
| `/` | ランディング（Hero / Features / API プレビュー / Pricing / Footer） |
| `/law` | 特定商取引法に基づく表記（審査用・プレースホルダ） |
| `/tokushoho` | `/law` へリダイレクト |
| `/legal` | 旧版（必要に応じて維持） |
| `/terms` | 利用規約 |
| `/privacy` | プライバシーポリシー |

## 本番ビルド

```bash
npm run build
npm start
```

Vercel では **Root Directory** を `web` に設定するか、モノレポ用の設定でこのディレクトリをデプロイ対象にしてください。
