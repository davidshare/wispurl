import { Eyebrow } from "@/components/brand/eyebrow";

/** Placeholder — per-link analytics and charts are built in a later prompt. */
export default function AnalyticsPage() {
  return (
    <div className="space-y-4 p-6 md:p-8">
      <Eyebrow>Analytics</Eyebrow>
      <p className="max-w-xl text-base leading-relaxed text-muted-foreground">
        Clicks over time, top referrers, and per-link breakdowns will appear here.
      </p>
    </div>
  );
}
