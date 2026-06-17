import { Skeleton } from "@/components/ui/skeleton";

/**
 * Group-level loading UI. The sidebar + topbar (from the layout) stay mounted, so
 * only this content area swaps in — no layout shift. The skeletons roughly match a
 * typical page's header + card grid.
 */
export default function DashboardLoading() {
  return (
    <div className="space-y-6 p-6 md:p-8">
      <Skeleton className="h-9 w-48" />
      <Skeleton className="h-5 w-72" />
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <Skeleton key={index} className="h-32 rounded-2xl" />
        ))}
      </div>
    </div>
  );
}
