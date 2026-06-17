import { Eyebrow } from "@/components/brand/eyebrow";
import { Reveal } from "@/components/marketing/reveal";
import { AnalyticsChart } from "@/components/marketing/analytics-chart";

const STATS = [
  { value: "12,480", label: "clicks this week" },
  { value: "+24%", label: "vs. last week", accent: true },
  { value: "launch", label: "top short code", violet: true },
];

/**
 * Dark feature band — the page's contrast moment. The whole section opts into the
 * `dark` token set (so it stays ink-dark in light mode too), with a violet chart
 * and mono numbers showing the analytics capability.
 */
export function AnalyticsBand() {
  return (
    <section className="dark bg-background text-foreground">
      <div className="mx-auto grid w-full max-w-[1200px] items-center gap-12 px-6 py-24 md:grid-cols-2 md:py-32">
        <Reveal className="space-y-6">
          <Eyebrow>Live analytics</Eyebrow>
          <h2 className="font-heading text-h2 font-bold">
            See every click — not just that someone clicked.
          </h2>
          <p className="max-w-md text-base leading-relaxed text-muted-foreground">
            Totals, daily trends, and top referrers for each link, updated as the
            clicks land. The numbers are the product.
          </p>
          <dl className="flex flex-wrap gap-8 pt-2">
            {STATS.map((stat) => (
              <div key={stat.label} className="space-y-1">
                <dd
                  className={`font-mono text-3xl font-bold ${
                    stat.accent
                      ? "text-signal"
                      : stat.violet
                        ? "text-violet"
                        : "text-foreground"
                  }`}
                >
                  {stat.value}
                </dd>
                <dt className="text-xs text-muted-foreground">{stat.label}</dt>
              </div>
            ))}
          </dl>
        </Reveal>

        <Reveal delayMs={120}>
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm">
            <div className="mb-4 flex items-center justify-between font-mono text-xs text-muted-foreground">
              <span>Clicks · last 8 days</span>
              <span className="text-violet">wisp.url/launch</span>
            </div>
            <AnalyticsChart />
          </div>
        </Reveal>
      </div>
    </section>
  );
}
