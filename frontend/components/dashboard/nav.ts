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
  { title: "Links", href: "/links", Icon: Link2 },
  { title: "Analytics", href: "/analytics", Icon: BarChart3 },
  { title: "Settings", href: "/settings", Icon: Settings },
];

/** Map a pathname to the topbar page title. */
export function pageTitle(pathname: string): string {
  const match = DASHBOARD_NAV.find(
    (item) => pathname === item.href || pathname.startsWith(`${item.href}/`),
  );
  return match?.title ?? "Dashboard";
}
