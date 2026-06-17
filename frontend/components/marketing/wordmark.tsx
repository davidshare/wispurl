import Link from "next/link";
import { cn } from "@/lib/utils";

/** The WispURL wordmark: mono, lowercase, with "url" in signal. */
export function Wordmark({ className }: { className?: string }) {
  return (
    <Link
      href="/"
      aria-label="WispURL home"
      className={cn(
        "rounded-sm font-mono text-lg font-bold lowercase tracking-tight focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
        className,
      )}
    >
      wisp<span className="text-signal">url</span>
    </Link>
  );
}
