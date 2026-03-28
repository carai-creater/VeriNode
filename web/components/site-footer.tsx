import Link from "next/link";

const links = [
  { href: "/law", label: "特定商取引法に基づく表記" },
  { href: "/terms", label: "利用規約" },
  { href: "/privacy", label: "プライバシーポリシー" },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-white/10 bg-zinc-950">
      <div className="mx-auto max-w-6xl px-4 py-12 sm:px-6">
        <div className="flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-lg font-semibold text-white">VeriNode</p>
            <p className="mt-1 max-w-sm text-sm text-zinc-500">
              AI の回答に、確かな根拠を。ウェブ検索ベースのファクトチェック API。
            </p>
          </div>
          <nav className="flex flex-col gap-3 sm:text-right">
            {links.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                className="text-sm text-zinc-400 transition hover:text-brand-400"
              >
                {l.label}
              </Link>
            ))}
          </nav>
        </div>
        <p className="mt-10 text-center text-xs text-zinc-600">
          © {new Date().getFullYear()} VeriNode. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
