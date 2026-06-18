"use client";

import { Link2 } from "lucide-react";
import { Eyebrow } from "@/components/brand/eyebrow";
import { Skeleton } from "@/components/ui/skeleton";
import { SummaryCards } from "@/components/dashboard/summary-cards";
import { RecentLinks } from "@/components/dashboard/recent-links";
import { EmptyState } from "@/components/dashboard/empty-state";
import { CreateLinkButton } from "@/components/dashboard/create-link-button";
import { useLinks } from "@/lib/query/links";

export default function DashboardPage() {
  const { data, isPending, isError } = useLinks({ limit: 50, offset: 0 });

  return (
    <div className="space-y-8 p-6 md:p-8">
      <div className="space-y-3">
        <Eyebrow>Dashboard</Eyebrow>
        <h2 className="font-heading text-display-lg font-bold">Overview</h2>
      </div>

      {isPending ? (
        <div className="space-y-8">
          <div className="grid gap-4 sm:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <Skeleton key={index} className="h-28 rounded-2xl" />
            ))}
          </div>
          <Skeleton className="h-64 rounded-2xl" />
        </div>
      ) : isError ? (
        <p className="rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
          We couldn&apos;t load your dashboard. Refresh to try again.
        </p>
      ) : data.total === 0 ? (
        <EmptyState
          Icon={Link2}
          title="Create your first link"
          description="Paste a long URL, get a short one back, and watch the clicks roll in."
          action={<CreateLinkButton />}
        />
      ) : (
        <div className="space-y-10">
          <SummaryCards links={data.items} total={data.total} />
          <RecentLinks items={data.items.slice(0, 5)} />
        </div>
      )}
    </div>
  );
}
