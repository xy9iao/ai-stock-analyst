"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { Candle, HistoryRange } from "@/lib/api/market";
import { parseNum } from "@/lib/format";

type ChartPoint = { label: string; price: number; volume: number };

function toLabel(timestamp: string, range: HistoryRange): string {
  const d = new Date(timestamp);
  if (range === "1d" || range === "1w") {
    return d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  }
  return d.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

export function StockPriceChart({
  candles,
  range,
}: {
  candles: Candle[];
  range: HistoryRange;
}) {
  if (candles.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-md border border-dashed border-slate-300 text-sm text-slate-500">
        No chart data for this range.
      </div>
    );
  }

  const data: ChartPoint[] = candles.map((c) => ({
    label: toLabel(c.timestamp, range),
    price: parseNum(c.close) ?? 0,
    volume: c.volume,
  }));

  return (
    <div className="flex flex-col gap-2">
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 0, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="label" tick={{ fontSize: 11 }} minTickGap={32} />
          <YAxis domain={["auto", "auto"]} tick={{ fontSize: 11 }} width={56} />
          <Tooltip />
          <Area type="monotone" dataKey="price" stroke="#047857" fill="#d1fae5" />
        </AreaChart>
      </ResponsiveContainer>
      <ResponsiveContainer width="100%" height={90}>
        <BarChart data={data} margin={{ top: 0, right: 8, bottom: 0, left: 8 }}>
          <XAxis dataKey="label" hide />
          <YAxis tick={{ fontSize: 11 }} width={56} />
          <Tooltip />
          <Bar dataKey="volume" fill="#94a3b8" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
