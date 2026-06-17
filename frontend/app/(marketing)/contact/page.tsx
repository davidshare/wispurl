import type { Metadata } from "next";
import { Eyebrow } from "@/components/brand/eyebrow";
import { Reveal } from "@/components/marketing/reveal";
import { ContactForm } from "@/components/marketing/contact-form";
import { buildMetadata } from "@/lib/seo";

export function generateMetadata(): Metadata {
  return buildMetadata({
    title: "Contact",
    description:
      "Questions, feedback, or partnership ideas? Send the WispURL team a message.",
    path: "/contact",
  });
}

export default function ContactPage() {
  return (
    <section className="mx-auto w-full max-w-[1200px] px-6">
      <div className="grid gap-12 py-24 sm:py-28 md:grid-cols-2">
        <Reveal className="space-y-6">
          <Eyebrow>Contact</Eyebrow>
          <h1 className="font-heading text-display-lg font-bold">
            Say hello.
          </h1>
          <p className="max-w-md text-lg leading-relaxed text-muted-foreground">
            Questions, feedback, or an idea for what WispURL should do next?
            We&apos;d love to hear it.
          </p>
        </Reveal>

        <Reveal
          delayMs={120}
          className="rounded-2xl border border-border bg-card p-8 shadow-sm"
        >
          <ContactForm />
        </Reveal>
      </div>
    </section>
  );
}
