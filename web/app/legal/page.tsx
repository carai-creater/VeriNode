import type { Metadata } from "next";
import Link from "next/link";
import { LegalShell } from "@/components/legal-shell";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "特定商取引法に基づく表記 | VeriNode",
  description: "VeriNode の特定商取引法に基づく表記です。",
};

export default function LegalPage() {
  return (
    <>
      <LegalShell title="特定商取引法に基づく表記">
        <p className="text-zinc-400">
          ストライプ（Stripe）等の決済審査に必要な事項を、以下のとおり表示します。お申し込みはウェブサイト上からオンラインで行います。販売価格の詳細は{" "}
          <Link href="/#pricing" className="text-brand-400 hover:underline">
            料金ページ
          </Link>
          をご確認ください。
        </p>
        <p className="text-sm text-zinc-500">
          所在地は本ページ上では表示しておりません。法令に基づく開示請求があった場合は、下記メールにて対応します。
        </p>
        <div className="overflow-x-auto rounded-xl border border-white/10">
          <table className="w-full min-w-[28rem] text-left text-sm">
            <tbody className="divide-y divide-white/10">
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  販売業者
                </th>
                <td className="px-4 py-3 text-zinc-200">林 連太郎</td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  代表責任者
                </th>
                <td className="px-4 py-3 text-zinc-200">林 連太郎</td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  電話番号
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  電話番号の掲載は行っておりません。ご請求があった場合は、メールにて開示します。
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  メールアドレス
                </th>
                <td className="px-4 py-3">
                  <a
                    href="mailto:carai@cocarai.com"
                    className="text-brand-400 hover:underline"
                  >
                    carai@cocarai.com
                  </a>
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  販売価格
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  各プランの紹介ページ（
                  <Link href="/#pricing" className="text-brand-400 hover:underline">
                    料金
                  </Link>
                  ）に記載のとおりです。従量課金を併用する場合は、決済完了前に Stripe Checkout
                  に表示される金額が適用されます。
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  商品代金以外の必要料金
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  なし（インターネット接続料金等はお客様のご負担となります）。
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  支払方法
                </th>
                <td className="px-4 py-3 text-zinc-200">クレジットカード決済（Stripe）</td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  支払時期
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  初回はお申し込み時（サブスクリプションの場合）、次回以降は各更新日に自動課金されます。従量課金は都度、利用に応じて決済が発生します。
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  商品の引渡時期
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  お支払い完了後、即時（API 応答としてサービスを提供します）。
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  返品・交換・キャンセル
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  デジタルコンテンツの性質上、提供完了後の返金・返品はお受けできません。法令により義務付けられる場合を除きます。サブスクリプションの解約は、お客様のダッシュボード（アカウント設定）からいつでも可能です。従量課金については、課金が発生した取引の性質に応じて取扱います。
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-zinc-500">
          表記の変更は本ページをもって告知するものとし、変更後にご利用いただいた場合、変更後の内容に同意したものとみなします。
        </p>
      </LegalShell>
      <SiteFooter />
    </>
  );
}
