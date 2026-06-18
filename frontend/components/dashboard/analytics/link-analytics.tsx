"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CopyButton } from "@/components/dashboard/copy-button";
import { QrButton } from "@/components/dashboard/qr-button";
import { LinkStatusBadge, formatDate } from "@/components/dashboard/link-status";
import { TopReferrers } from "@/components/dashboard/analytics/top-referrers";
import { useLinks } from "@/lib/query/links";
import { useStats } from "@/lib/query/stats";

// Lazy-load the Recharts-based chart so its (heavy) bundle isn't in the route's
// initial JS; a skeleton holds the space (no layout shift).
const ClicksChart = dynamic(
  () =>
    import("@/components/dashboard/analytics/clicks-chart").then((m) => ({
      default: m.ClicksChart,
    })),
  {
    ssr: false,
    loading: () => <Skeleton className="h-64 w-full rounded-xl" />,
  },
);

function BackLink() {
  return (
    <Link
      href="/dashboard/links"
      className="inline-flex items-center gap-1 rounded-sm text-sm text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      <ArrowLeft className="size-4" />
      Back to links
    </Link>
  );
}

function Stat({
  label,
  value,
  big = false,
}: {
  label: string;
  value: string;
  big?: boolean;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6">
      <p className="font-mono text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
        {label}
      </p>
      <p
        className={`mt-2 font-heading font-bold tabular-nums ${
          big ? "text-display-lg" : "text-h2"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function Notice({ title, body }: { title: string; body: string }) {
  return (
    <div className="space-y-6 p-6 md:p-8">
      <BackLink />
      <div className="rounded-2xl border border-border bg-card p-10 text-center">
        <h2 className="font-heading text-h2 font-bold">{title}</h2>
        <p className="mt-2 text-sm text-muted-foreground">{body}</p>
      </div>
    </div>
  );
}

export function LinkAnalytics({ shortCode }: { shortCode: string }) {
  const linksQuery = useLinks({ limit: 50, offset: 0 });
  const statsQuery = useStats(shortCode);

  const link = linksQuery.data?.items.find(
    (item) => item.short_code === shortCode,
  );
  // Loaded the list but this code isn't in it → treat as deleted/not yours.
  const linkMissing = linksQuery.data !== undefined && !link;

  if (statsQuery.isPending || linksQuery.isPending) {
    return (
      <div className="space-y-8 p-6 md:p-8">
        <Skeleton className="h-5 w-28" />
        <Skeleton className="h-9 w-40" />
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, index) => (
            <Skeleton key={index} className="h-28 rounded-2xl" />
          ))}
        </div>
        <Skeleton className="h-64 rounded-2xl" />
      </div>
    );
  }

  if (linkMissing) {
    return (
      <Notice
        title="This link no longer exists."
        body="It may have been deleted. Head back to your links to create a new one."
      />
    );
  }

  if (statsQuery.isError) {
    return (
      <Notice
        title="We couldn't load analytics."
        body="Something went wrong fetching this link's data. Refresh to try again."
      />
    );
  }

  const stats = statsQuery.data;
  const shortUrl = link?.short_url || shortCode;
  const bestDay = stats.clicks_by_day.reduce<{ date: string; count: number } | null>(
    (best, day) => (day.count > (best?.count ?? -1) ? day : best),
    null,
  );

  return (
    <div className="space-y-8 p-6 md:p-8">
      <BackLink />

      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-3">
          <span className="font-mono text-2xl font-bold text-signal">
            {shortCode}
          </span>
          {link ? <LinkStatusBadge link={link} /> : null}
        </div>
        {link ? (
          <a
            href={link.long_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex max-w-xl items-center gap-1 text-sm text-muted-foreground hover:text-foreground"
          >
            <span className="truncate">{link.long_url}</span>
            <ExternalLink className="size-3 shrink-0" />
          </a>
        ) : null}
        <div className="flex items-center gap-2">
          <CopyButton value={shortUrl} label="Copy short link" />
          {link ? (
            <Button variant="outline" size="icon" aria-label="Open link" asChild>
              <a href={link.long_url} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="size-4" />
              </a>
            </Button>
          ) : null}
          <QrButton shortCode={shortCode} shortUrl={shortUrl} />
        </div>
      </header>

      {stats.total_clicks === 0 ? (
        <div className="space-y-4 rounded-2xl border border-dashed border-border bg-card/50 p-10 text-center">
          <h2 className="font-heading text-h3 font-medium">No clicks yet</h2>
          <p className="mx-auto max-w-sm text-sm text-muted-foreground">
            Share your link to start seeing data here.
          </p>
          <div className="flex items-center justify-center gap-2">
            <code className="rounded-lg border border-border bg-muted px-3 py-2 font-mono text-sm">
              {shortUrl}
            </code>
            <CopyButton value={shortUrl} label="Copy short link" />
          </div>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <Stat
              label="Total clicks"
              value={stats.total_clicks.toLocaleString()}
              big
            />
            <Stat
              label="Best day"
              value={
                bestDay
                  ? `${formatDate(bestDay.date)} · ${bestDay.count.toLocaleString()}`
                  : "—"
              }
            />
            <Stat
              label="Referrers"
              value={stats.top_referrers.length.toLocaleString()}
            />
          </div>
          <div className="rounded-2xl border border-border bg-card p-6">
            <ClicksChart data={stats.clicks_by_day} />
          </div>
          <div className="rounded-2xl border border-border bg-card p-6">
            <TopReferrers referrers={stats.top_referrers} />
          </div>
        </>
      )}
    </div>
  );
}
