"use client";

import {
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";

import type { LeaderboardRow } from "@/lib/results";

type Props = {
  rows: LeaderboardRow[];
};

export function ParetoChart({ rows }: Props) {
  const data = rows.map((row) => ({
    system: row.system,
    x: row.p95,
    y: row.f1,
  }));
  return (
    <div className="h-80 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 16, right: 16, bottom: 32, left: 32 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            type="number"
            dataKey="x"
            name="p95 latency"
            unit="ms"
            label={{ value: "p95 latency (ms)", position: "bottom" }}
          />
          <YAxis
            type="number"
            dataKey="y"
            name="F1"
            domain={[0, 1]}
            label={{ value: "F1", angle: -90, position: "insideLeft" }}
          />
          <ZAxis dataKey="system" name="System" />
          <Tooltip cursor={{ strokeDasharray: "3 3" }} />
          <Legend />
          <Scatter name="Systems" data={data} fill="#4F46E5" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
