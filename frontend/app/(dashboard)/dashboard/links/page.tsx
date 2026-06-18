import { Eyebrow } from "@/components/brand/eyebrow";
import { LinksTable } from "@/components/dashboard/links-table";

export default function LinksPage() {
  return (
    <div className="space-y-6 p-6 md:p-8">
      <div className="space-y-3">
        <Eyebrow>Links</Eyebrow>
        <p className="max-w-xl text-sm text-muted-foreground">
          Copy, share, generate a QR code, or delete — all your short links live
          here.
        </p>
      </div>
      <LinksTable />
    </div>
  );
}
