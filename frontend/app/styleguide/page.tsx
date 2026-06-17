import { SiteHeader } from "@/components/site-header";
import { Eyebrow } from "@/components/brand/eyebrow";
import { Highlight } from "@/components/brand/highlight";
import { CompressionMeter } from "@/components/brand/compression-meter";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const BRAND_COLORS = [
  { name: "ink", className: "bg-ink", hex: "#0B0F14" },
  { name: "paper", className: "bg-paper", hex: "#FCFCFA" },
  { name: "signal", className: "bg-signal", hex: "#FF5A1F" },
  { name: "violet", className: "bg-violet", hex: "#5B43F5" },
  { name: "mist", className: "bg-mist", hex: "#EEF0F2" },
];

const SEMANTIC_COLORS = [
  { name: "background", className: "bg-background" },
  { name: "foreground", className: "bg-foreground" },
  { name: "primary", className: "bg-primary" },
  { name: "secondary", className: "bg-secondary" },
  { name: "muted", className: "bg-muted" },
  { name: "accent", className: "bg-accent" },
  { name: "border", className: "bg-border" },
  { name: "ring", className: "bg-ring" },
];

function Section({
  eyebrow,
  title,
  band,
  children,
}: {
  eyebrow: string;
  title: string;
  band?: boolean;
  children: React.ReactNode;
}) {
  return (
    <section className={band ? "bg-mist dark:bg-card" : "bg-background"}>
      <div className="mx-auto w-full max-w-[1200px] space-y-8 px-6 py-20">
        <div className="space-y-3">
          <Eyebrow>{eyebrow}</Eyebrow>
          <h2 className="font-heading text-h2 font-bold">{title}</h2>
        </div>
        {children}
      </div>
    </section>
  );
}

export default function StyleguidePage() {
  return (
    <>
      <SiteHeader />
      <main>
        <div className="mx-auto w-full max-w-[1200px] space-y-6 px-6 py-20">
          <Eyebrow>Ink &amp; Signal</Eyebrow>
          <h1 className="font-heading text-display-lg font-bold">
            WispURL <Highlight>styleguide</Highlight>
          </h1>
          <p className="max-w-xl text-lg leading-relaxed text-muted-foreground">
            The tokens, type, and signature devices that make up the brand. A
            link is something you compress.
          </p>
          <CompressionMeter className="max-w-md" />
        </div>

        <Section eyebrow="Color" title="Palette" band>
          <div>
            <h3 className="mb-4 font-heading text-h3 font-medium">Brand</h3>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
              {BRAND_COLORS.map((c) => (
                <div key={c.name} className="space-y-2">
                  <div
                    className={`${c.className} h-20 rounded-2xl border border-border`}
                  />
                  <div className="font-mono text-xs">
                    <div className="font-bold">{c.name}</div>
                    <div className="text-muted-foreground">{c.hex}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <h3 className="mb-4 font-heading text-h3 font-medium">Semantic</h3>
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {SEMANTIC_COLORS.map((c) => (
                <div key={c.name} className="space-y-2">
                  <div
                    className={`${c.className} h-16 rounded-xl border border-border`}
                  />
                  <div className="font-mono text-xs text-muted-foreground">
                    {c.name}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </Section>

        <Section eyebrow="Type" title="Type scale">
          <div className="space-y-6">
            <p className="font-heading text-display-xl font-bold">
              Display xl
            </p>
            <p className="font-heading text-display-lg font-bold">Display lg</p>
            <p className="font-heading text-h2 font-bold">Heading 2</p>
            <p className="font-heading text-h3 font-medium">Heading 3</p>
            <p className="text-base leading-relaxed">
              Body — Inter at a relaxed 1.6 line height for comfortable reading.
            </p>
            <p className="text-sm text-muted-foreground">
              Small — secondary copy and captions.
            </p>
            <p className="font-mono text-base font-medium">
              Mono — wisp.url/a1b2c3 (data is the brand)
            </p>
          </div>
        </Section>

        <Section eyebrow="Components" title="Buttons" band>
          <div className="flex flex-wrap items-center gap-3">
            <Button>Create link</Button>
            <Button variant="signal">Primary CTA</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="ghost">Ghost</Button>
            <Button variant="destructive">Delete</Button>
            <Button variant="link">Link</Button>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Button size="sm">Small</Button>
            <Button>Default</Button>
            <Button size="lg" variant="signal">
              Large CTA
            </Button>
          </div>
          <p className="text-sm text-muted-foreground">
            Default is the dark ink pill. Signal-orange is reserved for the one
            primary CTA per view.
          </p>
        </Section>

        <Section eyebrow="Devices" title="Signature devices">
          <div className="grid gap-6 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="font-heading">Eyebrow</CardTitle>
                <CardDescription>
                  Uppercase mono + a 24px rule, above section headings.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Eyebrow>Top referrers</Eyebrow>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="font-heading">Highlight box</CardTitle>
                <CardDescription>
                  One word per headline, at most once per page.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="font-heading text-h3 font-bold">
                  Keep it <Highlight>short</Highlight>
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="font-heading">
                  Compression meter
                </CardTitle>
                <CardDescription>
                  A 2px bar that fills left-to-right. Loading + accent motif.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <CompressionMeter />
                <CompressionMeter loop />
              </CardContent>
            </Card>
          </div>
        </Section>

        <Section eyebrow="Data" title="Short code treatment" band>
          <div className="flex flex-col gap-2 font-mono text-2xl">
            <div>
              <span className="text-muted-foreground">wisp.url/</span>
              <span className="font-bold text-foreground">a1b2c3</span>
            </div>
            <div>
              <span className="text-muted-foreground">wisp.url/</span>
              <span className="font-bold text-signal">launch</span>
            </div>
          </div>
        </Section>
      </main>
    </>
  );
}
