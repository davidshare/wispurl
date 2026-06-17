"use client";

import { Area, AreaChart, ResponsiveContainer } from "recharts";

// Clicks over the last 8 days. Concrete violet (the band is always dark, so the
// brightened dark-mode violet is the right constant here).
const VIOLET = "oklch(0.66 0.21 280)";

const DATA = [
  { day: "Mon", clicks: 120 },
  { day: "Tue", clicks: 210 },
  { day: "Wed", clicks: 180 },
  { day: "Thu", clicks: 320 },
  { day: "Fri", clicks: 290 },
  { day: "Sat", clicks: 460 },
  { day: "Sun", clicks: 540 },
  { day: "Mon", clicks: 720 },
];

/** Small animated violet area chart for the dark analytics band. */
export function AnalyticsChart() {
  return (
    <div className="h-48 w-full" aria-hidden>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={DATA} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
          <defs>
            <linearGradient id="clicksFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={VIOLET} stopOpacity={0.5} />
              <stop offset="100%" stopColor={VIOLET} stopOpacity={0} />
            </linearGradient>
          </defs>
          <Area
            type="monotone"
            dataKey="clicks"
            stroke={VIOLET}
            strokeWidth={2}
            fill="url(#clicksFill)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
