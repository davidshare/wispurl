import { Eyebrow } from "@/components/brand/eyebrow";

/**
 * Marketing home — shell only. Blank paper page with no sections yet (sections are
 * built in later prompts). The min-height lets the sticky header's scroll/blur be
 * exercised before the footer.
 */
export default function MarketingHome() {
  return (
    <div className="mx-auto flex min-h-[140vh] w-full max-w-[1200px] flex-col items-start gap-4 px-6 py-24">
      <Eyebrow>Marketing</Eyebrow>
      <p className="font-mono text-sm text-muted-foreground">
        Shell only — sections land in a later prompt.
      </p>
    </div>
  );
}
