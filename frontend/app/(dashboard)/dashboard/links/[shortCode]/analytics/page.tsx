import { LinkAnalytics } from "@/components/dashboard/analytics/link-analytics";

/** Per-link analytics. Thin server wrapper that unwraps params for the client view. */
export default async function LinkAnalyticsPage({
  params,
}: {
  params: Promise<{ shortCode: string }>;
}) {
  const { shortCode } = await params;
  return <LinkAnalytics shortCode={decodeURIComponent(shortCode)} />;
}
