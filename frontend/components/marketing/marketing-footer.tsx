import Link from "next/link";
import { AtSign, Globe, Mail, Rss } from "lucide-react";
import { Wordmark } from "@/components/marketing/wordmark";
import { FOOTER_COMPANY, FOOTER_PRODUCT, type NavItem } from "@/components/marketing/nav";
import { cn } from "@/lib/utils";

const focusRing =
  "rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background";

const SOCIALS = [
  { label: "Website", href: "#", Icon: Globe },
  { label: "Social", href: "#", Icon: AtSign },
  { label: "Email", href: "#", Icon: Mail },
  { label: "Blog", href: "#", Icon: Rss },
];

function FooterColumn({ title, items }: { title: string; items: NavItem[] }) {
  return (
    <div>
      <h2 className="mb-3 font-mono text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
        {title}
      </h2>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item.href}>
            <Link
              href={item.href}
              className={cn(
                "text-sm text-muted-foreground transition-colors hover:text-foreground",
                focusRing,
              )}
            >
              {item.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}

/** Quiet footer on mist: product/company links, social icons, copyright. */
export function MarketingFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-border bg-mist dark:bg-card">
      <div className="mx-auto grid w-full max-w-[1200px] gap-10 px-6 py-16 sm:grid-cols-2 md:grid-cols-4">
        <div className="space-y-3">
          <Wordmark />
          <p className="max-w-xs text-sm text-muted-foreground">
            Compress your links and see what happens after the click.
          </p>
        </div>

        <FooterColumn title="Product" items={FOOTER_PRODUCT} />
        <FooterColumn title="Company" items={FOOTER_COMPANY} />

        <div>
          <h2 className="mb-3 font-mono text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
            Elsewhere
          </h2>
          <ul className="flex items-center gap-2">
            {SOCIALS.map(({ label, href, Icon }) => (
              <li key={label}>
                <Link
                  href={href}
                  aria-label={label}
                  className={cn(
                    "flex size-9 items-center justify-center rounded-full border border-border text-muted-foreground transition-colors hover:text-foreground",
                    focusRing,
                  )}
                >
                  <Icon className="size-4" />
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="border-t border-border/60">
        <div className="mx-auto w-full max-w-[1200px] px-6 py-6">
          <p className="text-xs text-muted-foreground">
            © {year} WispURL. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}
