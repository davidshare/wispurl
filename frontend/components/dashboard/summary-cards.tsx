"use client";

import { useQueries } from "@tanstack/react-query";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { statsQueryOptions } from "@/lib/query/stats";
import type { Link } from "@/lib/api/types";

function StatCard({
  label,
  value,
  mono = false,
}: {
  label: string;
  value: string;
  mono?: boolean;
}) {
  return (
    <Card>
      <CardHeader className="pb-0">
        <span className="font-mono text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
          {label}
        </span>
      </CardHeader>
      <CardContent>
        <p
          className={`font-heading text-display-lg font-bold ${
            mono ? "font-mono text-h2" : ""
          }`}
        >
          {value}
        </p>
      </CardContent>
    </Card>
  );
}

/**
 * Summary stats. Total links comes from the list; total clicks and the top link are
 * aggregated client-side from per-link /stats (there's no aggregate endpoint). The
 * aggregation covers the links passed in (the first page), which is noted as an
 * approximation when there are more than a page of links.
 */
export function SummaryCards({ links, total }: { links: Link[]; total: number }) {
  const statsResults = useQueries({
    queries: links.map((link) => statsQueryOptions(link.short_code)),
  });

  const totalClicks = statsResults.reduce(
    (sum, result) => sum + (result.data?.total_clicks ?? 0),
    0,
  );

  let topCode = "—";
  let topClicks = -1;
  links.forEach((link, index) => {
    const clicks = statsResults[index]?.data?.total_clicks ?? 0;
    if (clicks > topClicks) {
      topClicks = clicks;
      topCode = link.short_code;
    }
  });

  return (
    <div className="grid gap-4 sm:grid-cols-3">
      <StatCard label="Total links" value={String(total)} />
      <StatCard label="Total clicks" value={totalClicks.toLocaleString()} />
      <StatCard label="Top link" value={topClicks > 0 ? topCode : "—"} mono />
    </div>
  );
}
