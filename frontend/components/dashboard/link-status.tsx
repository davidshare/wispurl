import { Badge } from "@/components/ui/badge";
import type { Link } from "@/lib/api/types";

export type LinkStatus = "active" | "expired" | "inactive";

/**
 * Plain helper (not a component/hook) so the time-based check is allowed — calling
 * Date.now() directly in a component render would trip the React purity rule.
 */
export function linkStatus(link: Link): LinkStatus {
  if (!link.is_active) return "inactive";
  if (
    link.expires_at !== null &&
    new Date(link.expires_at).getTime() < Date.now()
  ) {
    return "expired";
  }
  return "active";
}

/** Render a link's status badge. */
export function LinkStatusBadge({ link }: { link: Link }) {
  const status = linkStatus(link);

  if (status === "active") {
    return (
      <Badge
        variant="outline"
        className="border-violet/30 bg-violet/10 text-violet"
      >
        Active
      </Badge>
    );
  }
  return (
    <Badge variant="outline" className="text-muted-foreground capitalize">
      {status}
    </Badge>
  );
}

/** Short, locale-aware created date. */
export function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
