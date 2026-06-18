import type { Metadata } from "next";
import { headers } from "next/headers";
import { Inter, JetBrains_Mono, Space_Grotesk } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { SITE_URL } from "@/lib/env";

// Self-hosted at build time by next/font. Inter = body/UI, Space Grotesk =
// headlines/big numbers, JetBrains Mono = short codes/URLs/stats (data is the brand).
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
  weight: ["500", "700"],
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  weight: ["500", "700"],
});

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: {
    default: "WispURL — compress your links",
    template: "%s — WispURL",
  },
  description:
    "WispURL shortens links and shows you what happens after the click.",
  applicationName: "WispURL",
  robots: { index: true, follow: true },
  openGraph: {
    type: "website",
    siteName: "WispURL",
    url: "/",
    title: "WispURL — compress your links",
    description:
      "WispURL shortens links and shows you what happens after the click.",
  },
  twitter: {
    card: "summary_large_image",
    title: "WispURL — compress your links",
    description:
      "WispURL shortens links and shows you what happens after the click.",
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  // Reading the per-request nonce (set in proxy.ts) opts rendering into dynamic so
  // Next stamps its scripts with the nonce — required for the strict, no-inline CSP.
  await headers();

  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${inter.variable} ${spaceGrotesk.variable} ${jetbrainsMono.variable} h-full`}
    >
      <body className="flex min-h-full flex-col">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
