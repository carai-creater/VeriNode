import Link from "next/link";

const nav = [
  { href: "#features", label: "機能" },
  { href: "#api", label: "API" },
  { href: "#pricing", label: "料金" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-zinc-950/80 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="text-lg font-semibold tracking-tight text-white">
          VeriNode
        </Link>
        <nav className="hidden items-center gap-8 text-sm font-medium text-zinc-400 sm:flex">
          {nav.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="transition hover:text-white"
            >
              {item.label}
            </a>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <Link
            href="/legal"
            className="hidden text-xs text-zinc-500 hover:text-zinc-300 sm:inline"
          >
            特商法
          </Link>
        </div>
      </div>
    </header>
  );
}
