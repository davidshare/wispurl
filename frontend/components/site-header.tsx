import Link from "next/link";
import { ThemeToggle } from "@/components/theme-toggle";

/** Minimal top bar: wordmark + theme toggle. Used by the placeholder pages. */
export function SiteHeader() {
  return (
    <header className="sticky top-0 z-10 border-b border-border bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-16 w-full max-w-[1200px] items-center justify-between px-6">
        <Link
          href="/"
          className="font-mono text-lg font-bold tracking-tight lowercase"
        >
          wisp<span className="text-signal">url</span>
        </Link>
        <nav className="flex items-center gap-2">
          <Link
            href="/styleguide"
            className="rounded-full px-3 py-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Styleguide
          </Link>
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}
