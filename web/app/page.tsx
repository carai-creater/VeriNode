import Link from "next/link";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import { docsUrl, verifyEndpoint } from "@/lib/site";

const curlSample = (endpoint: string) => `curl -X POST "${endpoint}" \\
  -H "Content-Type: application/json" \\
  -H "X-Payment-Proof: YOUR_CHECKOUT_SESSION_ID" \\
  -d '{"claim":"検証したい主張をここに"}'`;

export default function HomePage() {
  const docs = docsUrl();
  const verify = verifyEndpoint();

  return (
    <>
      <SiteHeader />
      <main>
        {/* Hero */}
        <section className="relative overflow-hidden border-b border-white/10">
          <div
            className="pointer-events-none absolute inset-0 opacity-40"
            style={{
              background:
                "radial-gradient(ellipse 80% 50% at 50% -20%, rgba(20,184,166,0.35), transparent)",
            }}
          />
          <div className="relative mx-auto max-w-6xl px-4 pb-24 pt-20 text-center sm:px-6 sm:pb-32 sm:pt-28">
            <p className="mb-4 text-xs font-semibold uppercase tracking-[0.2em] text-brand-400">
              Fact-check API for AI
            </p>
            <h1 className="text-balance text-4xl font-bold tracking-tight text-white sm:text-5xl md:text-6xl">
              AIの回答に、
              <br className="sm:hidden" />
              確かな根拠を。
            </h1>
            <p className="mx-auto mt-6 max-w-2xl text-lg text-zinc-400">
              ウェブ検索に基づく主張検証を、エージェントやバックエンドから{" "}
              <code className="rounded bg-white/10 px-1.5 py-0.5 font-mono text-sm text-brand-300">
                POST /verify
              </code>{" "}
              で。スコア・引用・要約を JSON で。
            </p>
            <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
              <a
                href={docs}
                className="inline-flex h-12 min-w-[200px] items-center justify-center rounded-full bg-brand-500 px-8 text-sm font-semibold text-zinc-950 shadow-lg shadow-brand-500/25 transition hover:bg-brand-400"
              >
                API 利用を始める
              </a>
              <a
                href="#api"
                className="inline-flex h-12 min-w-[200px] items-center justify-center rounded-full border border-white/15 bg-white/5 px-8 text-sm font-medium text-white transition hover:bg-white/10"
              >
                リクエスト例を見る
              </a>
            </div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="scroll-mt-20 border-b border-white/10 py-20 sm:py-28">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                主な機能
              </h2>
              <p className="mt-4 text-zinc-400">
                ダッシュボード画面や JSON レスポンスはイメージです（プレースホルダー）。
              </p>
            </div>
            <div className="mt-16 grid gap-12 lg:grid-cols-3">
              {[
                {
                  title: "リアルタイム・ウェブ検索による事実確認",
                  desc: "公開ウェブを検索し、主張と照合。エージェントの出力をその場で検証できます。",
                  label: "検索・検証プレビュー",
                },
                {
                  title: "信頼性スコアリング",
                  desc: "ソースの整合性を踏まえたスコアで、判断の補助に使える指標を返します。",
                  label: "スコア UI プレースホルダー",
                },
                {
                  title: "引用元エビデンスの自動抽出",
                  desc: "根拠となる URL や抜粋をまとめて返し、ユーザーへの説明にそのまま利用できます。",
                  label: "引用リスト プレースホルダー",
                },
              ].map((item) => (
                <div key={item.title} className="flex flex-col">
                  <div className="relative aspect-[16/10] overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-zinc-800/80 to-zinc-900/80">
                    <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 p-6 text-center">
                      <div className="h-10 w-10 rounded-lg bg-brand-500/20 ring-1 ring-brand-400/30" />
                      <span className="text-xs font-medium text-zinc-500">
                        {item.label}
                      </span>
                    </div>
                  </div>
                  <h3 className="mt-6 text-lg font-semibold text-white">{item.title}</h3>
                  <p className="mt-2 text-sm leading-relaxed text-zinc-400">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* API Reference */}
        <section id="api" className="scroll-mt-20 border-b border-white/10 py-20 sm:py-28">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                API リファレンス（プレビュー）
              </h2>
              <p className="mt-4 text-zinc-400">
                課金ゲート通過後は{" "}
                <code className="rounded bg-white/10 px-1.5 py-0.5 font-mono text-xs">
                  X-Payment-Proof
                </code>{" "}
                に Checkout Session ID を付与して呼び出します。
              </p>
            </div>
            <div className="mx-auto mt-12 max-w-3xl overflow-hidden rounded-2xl border border-white/10 bg-zinc-900/50 shadow-2xl">
              <div className="flex items-center gap-2 border-b border-white/10 bg-zinc-900 px-4 py-3">
                <span className="h-3 w-3 rounded-full bg-red-500/80" />
                <span className="h-3 w-3 rounded-full bg-amber-500/80" />
                <span className="h-3 w-3 rounded-full bg-emerald-500/80" />
                <span className="ml-2 font-mono text-xs text-zinc-500">curl</span>
              </div>
              <pre className="overflow-x-auto p-5 text-left">
                <code className="font-mono text-[13px] leading-relaxed text-brand-100">
                  {curlSample(verify)}
                </code>
              </pre>
            </div>
            <p className="mx-auto mt-6 max-w-2xl text-center text-xs text-zinc-500">
              エンドポイントは環境変数{" "}
              <code className="rounded bg-white/5 px-1 font-mono">NEXT_PUBLIC_API_BASE_URL</code>{" "}
              で差し替え可能です。未設定時はプレースホルダー URL が表示されます。
            </p>
          </div>
        </section>

        {/* Pricing */}
        <section id="pricing" className="scroll-mt-20 border-b border-white/10 py-20 sm:py-28">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
                料金体系
              </h2>
              <p className="mt-4 text-zinc-400">
                Stripe 審査用にプランを明示しています。実際の請求は Checkout に表示される内容が優先されます。
              </p>
            </div>
            <div className="mt-16 grid gap-8 lg:grid-cols-3">
              {[
                {
                  name: "Free",
                  price: "$0",
                  period: "",
                  desc: "お試し・開発用。月間リクエスト上限あり。",
                  cta: "無料で始める",
                  href: docs,
                  featured: false,
                },
                {
                  name: "Pro",
                  price: "$29",
                  period: "/ 月",
                  desc: "本番ワークロード向け。優先レートとサポート。",
                  cta: "Pro に申し込む",
                  href: docs,
                  featured: true,
                },
                {
                  name: "Enterprise",
                  price: "カスタム",
                  period: "",
                  desc: "SLA・専用環境・請求書払いなど。",
                  cta: "お問い合わせ",
                  href: "mailto:carai@cocarai.com?subject=VeriNode%20Enterprise%20Plan",
                  featured: false,
                },
              ].map((plan) => (
                <div
                  key={plan.name}
                  className={`relative flex flex-col rounded-2xl border p-8 ${
                    plan.featured
                      ? "border-brand-500/50 bg-brand-500/5 shadow-xl shadow-brand-500/10"
                      : "border-white/10 bg-zinc-900/30"
                  }`}
                >
                  {plan.featured && (
                    <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full bg-brand-500 px-3 py-0.5 text-xs font-semibold text-zinc-950">
                      Popular
                    </span>
                  )}
                  <h3 className="text-lg font-semibold text-white">{plan.name}</h3>
                  <p className="mt-4 flex items-baseline gap-0.5">
                    <span className="text-4xl font-bold text-white">{plan.price}</span>
                    {plan.period ? (
                      <span className="text-zinc-500">{plan.period}</span>
                    ) : null}
                  </p>
                  <p className="mt-4 flex-1 text-sm text-zinc-400">{plan.desc}</p>
                  <a
                    href={plan.href}
                    className={`mt-8 inline-flex h-11 items-center justify-center rounded-full text-sm font-semibold transition ${
                      plan.featured
                        ? "bg-brand-500 text-zinc-950 hover:bg-brand-400"
                        : "border border-white/15 bg-white/5 text-white hover:bg-white/10"
                    }`}
                  >
                    {plan.cta}
                  </a>
                </div>
              ))}
            </div>
            <p className="mx-auto mt-10 max-w-2xl text-center text-xs leading-relaxed text-zinc-500">
              従量課金（例: 1 リクエストあたりの API 利用料）を併用する場合は、
              <Link href="/legal" className="text-brand-400 underline-offset-2 hover:underline">
                特定商取引法に基づく表記
              </Link>
              および Checkout 画面の表示に従います。解約はアカウント設定（ダッシュボード）から随時可能です。
            </p>
          </div>
        </section>

        {/* CTA strip */}
        <section className="py-16">
          <div className="mx-auto max-w-6xl px-4 sm:px-6">
            <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-zinc-800/50 to-zinc-900/80 px-8 py-12 text-center sm:px-12">
              <h2 className="text-2xl font-bold text-white sm:text-3xl">
                まずは OpenAPI で試す
              </h2>
              <p className="mx-auto mt-3 max-w-xl text-zinc-400">
                Swagger でスキーマを確認し、エージェントに組み込んでください。
              </p>
              <a
                href={docs}
                className="mt-8 inline-flex h-12 items-center justify-center rounded-full bg-white px-8 text-sm font-semibold text-zinc-950 transition hover:bg-zinc-200"
              >
                /docs を開く
              </a>
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
