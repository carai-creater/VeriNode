import Link from "next/link";

export function LegalShell({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <>
      <header className="border-b border-white/10 bg-zinc-950/90 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-3xl items-center justify-between px-4 sm:px-6">
          <Link href="/" className="text-sm font-medium text-zinc-400 hover:text-white">
            ← トップへ
          </Link>
          <span className="text-xs text-zinc-600">VeriNode</span>
        </div>
      </header>
      <article className="mx-auto max-w-3xl px-4 py-12 sm:px-6 sm:py-16">
        <h1 className="text-3xl font-bold tracking-tight text-white">{title}</h1>
        <div className="mt-10 space-y-6 text-sm leading-relaxed text-zinc-300 [&_h2]:mt-12 [&_h2]:scroll-mt-20 [&_h2]:text-lg [&_h2]:font-semibold [&_h2]:text-white [&_h2]:first:mt-0 [&_p]:leading-relaxed [&_ul]:list-disc [&_ul]:space-y-2 [&_ul]:pl-5 [&_strong]:font-semibold [&_strong]:text-zinc-100">
          {children}
        </div>
      </article>
    </>
  );
}
