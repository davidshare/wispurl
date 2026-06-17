"use client";

import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";

// Two-tone engagement split. Tailwind `fill-*` utilities pull the brand tokens
// (so the donut tracks dark mode); the arcs animate in on mount (Recharts default).
const DATA = [
  { name: "Tracked", value: 68 },
  { name: "Converted", value: 32 },
];

/** Small animated donut for the value-band stat card (violet + signal). */
export function StatDonut() {
  return (
    <div className="size-36 shrink-0" aria-hidden>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={DATA}
            dataKey="value"
            innerRadius="64%"
            outerRadius="100%"
            startAngle={90}
            endAngle={-270}
            paddingAngle={3}
            stroke="none"
          >
            <Cell className="fill-violet" />
            <Cell className="fill-signal" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
