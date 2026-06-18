"use client";

import Link from "next/link";
import { BarChart3, ExternalLink, Link2 } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { CopyButton } from "@/components/dashboard/copy-button";
import { QrButton } from "@/components/dashboard/qr-button";
import { DeleteLinkButton } from "@/components/dashboard/delete-link-button";
import { CreateLinkButton } from "@/components/dashboard/create-link-button";
import { EmptyState } from "@/components/dashboard/empty-state";
import { LinkStatusBadge, formatDate } from "@/components/dashboard/link-status";
import { useLinks } from "@/lib/query/links";

export function LinksTable() {
  const { data, isPending, isError } = useLinks({ limit: 50, offset: 0 });

  if (isPending) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <Skeleton key={index} className="h-14 w-full rounded-xl" />
        ))}
      </div>
    );
  }

  if (isError) {
    return (
      <p className="rounded-xl border border-border bg-card p-6 text-sm text-muted-foreground">
        We couldn&apos;t load your links. Refresh to try again.
      </p>
    );
  }

  if (data.items.length === 0) {
    return (
      <EmptyState
        Icon={Link2}
        title="No links yet"
        description="Create your first short link and it'll show up here with its stats and QR code."
        action={<CreateLinkButton />}
      />
    );
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Short link</TableHead>
            <TableHead className="hidden md:table-cell">Destination</TableHead>
            <TableHead className="hidden sm:table-cell">Created</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.items.map((link) => (
            <TableRow key={link.id}>
              <TableCell>
                <div className="flex items-center gap-2">
                  <code className="max-w-[16ch] truncate font-mono text-sm font-medium md:max-w-[24ch]">
                    {link.short_url || link.short_code}
                  </code>
                  <CopyButton
                    value={link.short_url || link.short_code}
                    label="Copy short link"
                  />
                </div>
              </TableCell>
              <TableCell className="hidden md:table-cell">
                <a
                  href={link.long_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex max-w-[32ch] items-center gap-1 truncate text-sm text-muted-foreground hover:text-foreground"
                >
                  <span className="truncate">{link.long_url}</span>
                  <ExternalLink className="size-3 shrink-0" />
                </a>
              </TableCell>
              <TableCell className="hidden whitespace-nowrap text-sm text-muted-foreground sm:table-cell">
                {formatDate(link.created_at)}
              </TableCell>
              <TableCell>
                <LinkStatusBadge link={link} />
              </TableCell>
              <TableCell>
                <div className="flex items-center justify-end gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="View analytics"
                    asChild
                  >
                    <Link
                      href={`/dashboard/links/${link.short_code}/analytics`}
                    >
                      <BarChart3 className="size-4" />
                    </Link>
                  </Button>
                  <QrButton
                    shortCode={link.short_code}
                    shortUrl={link.short_url || link.short_code}
                  />
                  <DeleteLinkButton link={link} />
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
