"use client";

import * as React from "react";
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts";
import { useReducedMotion } from "framer-motion";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart";
import type { DailyClicks } from "@/lib/api/types";

// Mapped to the violet chart token; ChartContainer exposes it as --color-count,
// so the chart inherits the theme (and dark mode).
const chartConfig = {
  count: { label: "Clicks", color: "var(--chart-1)" },
} satisfies ChartConfig;

type Range = "7d" | "30d" | "all";

// Plain helper (not a component) so the Date.now() call is allowed.
function filterByRange(data: DailyClicks[], range: Range): DailyClicks[] {
  if (range === "all") return data;
  const days = range === "7d" ? 7 : 30;
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
  return data.filter((point) => new Date(point.date).getTime() >= cutoff);
}

function formatDay(value: string): string {
  return new Date(value).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

export function ClicksChart({ data }: { data: DailyClicks[] }) {
  const [range, setRange] = React.useState<Range>("30d");
  const reduceMotion = useReducedMotion();
  const filtered = filterByRange(data, range);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <h2 className="font-heading text-h3 font-medium">Clicks over time</h2>
        <Tabs value={range} onValueChange={(value) => setRange(value as Range)}>
          <TabsList>
            <TabsTrigger value="7d">7d</TabsTrigger>
            <TabsTrigger value="30d">30d</TabsTrigger>
            <TabsTrigger value="all">All</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Chart on >= sm; a compact list degrades onto tiny screens. */}
      <ChartContainer
        config={chartConfig}
        className="hidden aspect-[16/6] w-full sm:block"
      >
        <AreaChart data={filtered} margin={{ left: 12, right: 12 }}>
          <defs>
            <linearGradient id="fillCount" x1="0" y1="0" x2="0" y2="1">
              <stop
                offset="5%"
                stopColor="var(--color-count)"
                stopOpacity={0.4}
              />
              <stop
                offset="95%"
                stopColor="var(--color-count)"
                stopOpacity={0}
              />
            </linearGradient>
          </defs>
          <CartesianGrid vertical={false} />
          <XAxis
            dataKey="date"
            tickLine={false}
            axisLine={false}
            tickMargin={8}
            minTickGap={24}
            tickFormatter={formatDay}
          />
          <ChartTooltip content={<ChartTooltipContent />} />
          <Area
            dataKey="count"
            type="monotone"
            stroke="var(--color-count)"
            strokeWidth={2}
            fill="url(#fillCount)"
            isAnimationActive={!reduceMotion}
          />
        </AreaChart>
      </ChartContainer>

      <ul className="space-y-1 sm:hidden">
        {filtered.length === 0 ? (
          <li className="text-sm text-muted-foreground">
            No clicks in this range.
          </li>
        ) : (
          filtered.map((point) => (
            <li
              key={point.date}
              className="flex items-center justify-between font-mono text-sm"
            >
              <span className="text-muted-foreground">
                {formatDay(point.date)}
              </span>
              <span className="tabular-nums">
                {point.count.toLocaleString()}
              </span>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}
