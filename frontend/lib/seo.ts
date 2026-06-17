import type { Metadata } from "next";

/**
 * Build per-page metadata with Open Graph and explicit indexability. The title is
 * a bare string so the root layout's title template ("%s — WispURL") applies.
 */
export function buildMetadata({
  title,
  description,
  path,
}: {
  title: string;
  description: string;
  path: string;
}): Metadata {
  return {
    title,
    description,
    alternates: { canonical: path },
    robots: { index: true, follow: true },
    openGraph: {
      type: "website",
      siteName: "WispURL",
      url: path,
      title: `${title} — WispURL`,
      description,
    },
    twitter: {
      card: "summary_large_image",
      title: `${title} — WispURL`,
      description,
    },
  };
}
