import type { Metadata } from "next";
import Link from "next/link";
import { LegalShell } from "@/components/legal-shell";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "特定商取引法に基づく表記 | VeriNode",
  description: "特定商取引法に基づく表示（verinode.space）",
};

export default function LawPage() {
  return (
    <>
      <LegalShell title="特定商取引法に基づく表記">
        <p className="text-zinc-400">
          通信販売（デジタルサービス）に関する表示です。販売価格の詳細は{" "}
          <Link href="/#pricing" className="text-brand-400 hover:underline">
            料金ページ
          </Link>
          をご確認ください。
        </p>
        <p className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-xs text-amber-200/90">
          下記の <span className="font-mono text-amber-100">[ ]</span>{" "}
          内はプレースホルダです。デプロイ前にご自身の情報へ書き換えてください。
        </p>
        <div className="overflow-x-auto rounded-xl border border-white/10">
          <table className="w-full min-w-[28rem] text-left text-sm">
            <tbody className="divide-y divide-white/10">
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  販売業者
                </th>
                <td className="px-4 py-3 font-mono text-zinc-200">[会社名または個人名]</td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  代表責任者
                </th>
                <td className="px-4 py-3 font-mono text-zinc-200">[氏名]</td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  所在地
                </th>
                <td className="px-4 py-3 font-mono text-zinc-200">[郵便番号・住所]</td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  電話番号
                </th>
                <td className="px-4 py-3 font-mono text-zinc-200">[電話番号]</td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  メールアドレス
                </th>
                <td className="px-4 py-3 font-mono text-zinc-200">[メールアドレス]</td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  販売価格
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  各プランの紹介ページに記載
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  商品代金以外の必要料金
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  インターネット接続料金等（お客様のご負担）
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  支払方法
                </th>
                <td className="px-4 py-3 text-zinc-200">クレジットカード決済</td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  支払時期
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  初回購入時、および次月以降の更新時
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  商品の引き渡し時期
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  決済完了後、直ちにご利用いただけます。
                </td>
              </tr>
              <tr>
                <th className="whitespace-nowrap bg-zinc-900/50 px-4 py-3 font-medium text-zinc-400">
                  返品・交換・キャンセル
                </th>
                <td className="px-4 py-3 text-zinc-200">
                  デジタルコンテンツの特性上、返品・返金はできません。解約はいつでもマイページから可能です。
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="text-xs text-zinc-500">
          法令の改正やサービス内容の変更に伴い、本表示を更新することがあります。
        </p>
      </LegalShell>
      <SiteFooter />
    </>
  );
}
