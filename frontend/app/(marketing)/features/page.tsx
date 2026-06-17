import type { Metadata } from "next";
import { Eyebrow } from "@/components/brand/eyebrow";
import { Highlight } from "@/components/brand/highlight";
import { Reveal } from "@/components/marketing/reveal";
import { FeatureGrid } from "@/components/marketing/feature-grid";
import { AnalyticsBand } from "@/components/marketing/analytics-band";
import { CtaBand } from "@/components/marketing/cta-band";
import { buildMetadata } from "@/lib/seo";

export function generateMetadata(): Metadata {
  return buildMetadata({
    title: "Features",
    description:
      "Branded slugs, click tracking, QR codes, and safe redirects — everything WispURL does, in one place.",
    path: "/features",
  });
}

export default function FeaturesPage() {
  return (
    <>
      <section className="mx-auto w-full max-w-[1200px] px-6">
        <Reveal className="flex flex-col items-start gap-6 py-24 sm:py-28">
          <Eyebrow>Features</Eyebrow>
          <h1 className="max-w-3xl font-heading text-display-lg font-bold">
            Everything the link needs — nothing it{" "}
            <Highlight>doesn&apos;t</Highlight>.
          </h1>
          <p className="max-w-xl text-lg leading-relaxed text-muted-foreground">
            The whole toolkit: compress a URL, brand it, share it, and watch the
            clicks roll in.
          </p>
        </Reveal>
      </section>

      <FeatureGrid />
      <AnalyticsBand />
      <CtaBand />
    </>
  );
}
