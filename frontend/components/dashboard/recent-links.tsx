import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import { CopyButton } from "@/components/dashboard/copy-button";
import { LinkStatusBadge, formatDate } from "@/components/dashboard/link-status";
import type { Link as LinkModel } from "@/lib/api/types";

/** Compact "recent links" list for the dashboard home. */
export function RecentLinks({ items }: { items: LinkModel[] }) {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-heading text-h3 font-medium">Recent links</h2>
        <Link
          href="/dashboard/links"
          className="inline-flex items-center gap-1 rounded-sm text-sm text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
        >
          View all
          <ArrowUpRight className="size-3.5" />
        </Link>
      </div>

      <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border">
        {items.map((link) => (
          <li
            key={link.id}
            className="flex items-center gap-3 bg-card px-4 py-3"
          >
            <code className="min-w-0 flex-1 truncate font-mono text-sm font-medium">
              {link.short_url || link.short_code}
            </code>
            <LinkStatusBadge link={link} />
            <span className="hidden whitespace-nowrap text-xs text-muted-foreground sm:inline">
              {formatDate(link.created_at)}
            </span>
            <CopyButton
              value={link.short_url || link.short_code}
              label="Copy short link"
            />
          </li>
        ))}
      </ul>
    </section>
  );
}
