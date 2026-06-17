"use client";

import * as React from "react";
import dynamic from "next/dynamic";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

// Code-split: the dialog (form + zod + mutation) loads in its own chunk, only once
// the user first opens it.
const CreateLinkDialog = dynamic(
  () =>
    import("@/components/dashboard/create-link-dialog").then((m) => ({
      default: m.CreateLinkDialog,
    })),
  { ssr: false },
);

export function CreateLinkButton() {
  const [open, setOpen] = React.useState(false);
  const [mounted, setMounted] = React.useState(false);

  const onOpen = () => {
    setMounted(true);
    setOpen(true);
  };

  return (
    <>
      <Button variant="signal" onClick={onOpen}>
        <Plus className="size-4" />
        Create link
      </Button>
      {mounted ? (
        <CreateLinkDialog open={open} onOpenChange={setOpen} />
      ) : null}
    </>
  );
}
