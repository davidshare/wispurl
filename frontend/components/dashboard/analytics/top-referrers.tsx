import type { ReferrerCount } from "@/lib/api/types";

/** Horizontal bar list of top referrers (signal). Empty referrer → "Direct / none". */
export function TopReferrers({ referrers }: { referrers: ReferrerCount[] }) {
  const max = Math.max(1, ...referrers.map((entry) => entry.count));

  return (
    <div className="space-y-4">
      <h2 className="font-heading text-h3 font-medium">Top referrers</h2>
      {referrers.length === 0 ? (
        <p className="text-sm text-muted-foreground">No referrer data yet.</p>
      ) : (
        <ul className="space-y-3">
          {referrers.map((entry, index) => {
            const label =
              entry.referrer && entry.referrer.trim() !== ""
                ? entry.referrer
                : "Direct / none";
            const pct = Math.round((entry.count / max) * 100);
            return (
              <li key={`${label}-${index}`} className="space-y-1">
                <div className="flex items-center justify-between gap-2 text-sm">
                  <span className="truncate">{label}</span>
                  <span className="font-mono tabular-nums text-muted-foreground">
                    {entry.count.toLocaleString()}
                  </span>
                </div>
                <div className="h-2 w-full overflow-hidden rounded-full bg-mist">
                  <div
                    className="h-full rounded-full bg-signal"
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
