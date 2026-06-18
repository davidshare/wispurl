"use client";

import * as React from "react";
import { Download, QrCode } from "lucide-react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { API_PREFIX, API_URL } from "@/lib/env";

/** QR action: a dialog showing GET /qr/{short_code} as an image, with a download. */
export function QrButton({
  shortCode,
  shortUrl,
}: {
  shortCode: string;
  shortUrl: string;
}) {
  const src = `${API_URL}${API_PREFIX}/qr/${shortCode}`;

  const onDownload = async () => {
    try {
      const response = await fetch(src);
      if (!response.ok) throw new Error("Request failed");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `${shortCode}.png`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch {
      toast.error("Couldn't download the QR code.");
    }
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Show QR code">
          <QrCode className="size-4" />
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-xs">
        <DialogHeader>
          <DialogTitle className="font-heading">QR code</DialogTitle>
          <DialogDescription className="truncate font-mono text-xs">
            {shortUrl}
          </DialogDescription>
        </DialogHeader>
        <div className="flex justify-center">
          {/* eslint-disable-next-line @next/next/no-img-element -- dynamic cross-origin PNG from the gateway */}
          <img
            src={src}
            alt={`QR code for ${shortUrl}`}
            width={240}
            height={240}
            className="rounded-xl border border-border bg-white p-2"
          />
        </div>
        <DialogFooter>
          <Button variant="signal" className="w-full" onClick={onDownload}>
            <Download className="size-4" />
            Download PNG
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
