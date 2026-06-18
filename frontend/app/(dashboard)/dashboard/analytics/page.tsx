"use client";

import Link from "next/link";
import { ArrowUpRight, BarChart3 } from "lucide-react";
import { Eyebrow } from "@/components/brand/eyebrow";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/dashboard/empty-state";
import { CreateLinkButton } from "@/components/dashboard/create-link-button";
import { LinkStatusBadge } from "@/components/dashboard/link-status";
import { useLinks } from "@/lib/query/links";

export default function AnalyticsIndexPage() {
  const { data, isPending, isError } = useLinks({ limit: 50, offset: 0 });

  return (
    <div className="space-y-6 p-6 md:p-8">
      <div className="space-y-3">
        <Eyebrow>Analytics</Eyebrow>
        <p className="max-w-xl text-sm text-muted-foreground">
          Pick a link to see its clicks over time and top referrers.
        </p>
      </div>

      {isPending ? (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} className="h-14 w-full rounded-xl" />
          ))}
        </div>
      ) : isError ? (
        <p className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
          We couldn&apos;t load your links. Refresh to try again.
        </p>
      ) : data.items.length === 0 ? (
        <EmptyState
          Icon={BarChart3}
          title="Nothing to analyze yet"
          description="Create a link first, then come back to see how it performs."
          action={<CreateLinkButton />}
        />
      ) : (
        <ul className="divide-y divide-border overflow-hidden rounded-2xl border border-border">
          {data.items.map((link) => (
            <li key={link.id}>
              <Link
                href={`/dashboard/links/${link.short_code}/analytics`}
                className="flex items-center gap-3 bg-card px-4 py-3 transition-colors hover:bg-muted/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring"
              >
                <code className="min-w-0 flex-1 truncate font-mono text-sm font-medium">
                  {link.short_url || link.short_code}
                </code>
                <LinkStatusBadge link={link} />
                <ArrowUpRight className="size-4 shrink-0 text-muted-foreground" />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
