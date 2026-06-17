/** Marketing nav config, shared by the desktop nav and the mobile sheet. */

export interface NavItem {
  label: string;
  href: string;
}

// Section anchors on the marketing home (sections are built in a later prompt).
export const MARKETING_NAV: NavItem[] = [
  { label: "Features", href: "/#features" },
  { label: "About", href: "/#about" },
  { label: "Contact", href: "/#contact" },
];

export const FOOTER_PRODUCT: NavItem[] = [
  { label: "Features", href: "/#features" },
  { label: "Get started", href: "/signup" },
  { label: "Styleguide", href: "/styleguide" },
];

export const FOOTER_COMPANY: NavItem[] = [
  { label: "About", href: "/#about" },
  { label: "Contact", href: "/#contact" },
  { label: "Log in", href: "/login" },
];
