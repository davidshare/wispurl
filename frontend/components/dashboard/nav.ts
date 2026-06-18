import {
  BarChart3,
  LayoutDashboard,
  Link2,
  Settings,
  type LucideIcon,
} from "lucide-react";

export interface DashboardNavItem {
  title: string;
  href: string;
  Icon: LucideIcon;
}

export const DASHBOARD_NAV: DashboardNavItem[] = [
  { title: "Dashboard", href: "/dashboard", Icon: LayoutDashboard },
  { title: "Links", href: "/dashboard/links", Icon: Link2 },
  { title: "Analytics", href: "/dashboard/analytics", Icon: BarChart3 },
  { title: "Settings", href: "/dashboard/settings", Icon: Settings },
];

/**
 * Resolve the nav item for a pathname by LONGEST matching href, so a nested route
 * like /dashboard/links/abc/analytics matches "Links" rather than "Dashboard"
 * (which is a prefix of every dashboard route).
 */
export function matchNav(pathname: string): DashboardNavItem | undefined {
  return [...DASHBOARD_NAV]
    .sort((a, b) => b.href.length - a.href.length)
    .find(
      (item) =>
        pathname === item.href || pathname.startsWith(`${item.href}/`),
    );
}

/** The href of the active nav item (for highlighting), or null. */
export function activeNavHref(pathname: string): string | null {
  return matchNav(pathname)?.href ?? null;
}

/** Map a pathname to the topbar page title. */
export function pageTitle(pathname: string): string {
  return matchNav(pathname)?.title ?? "Dashboard";
}
