"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { StockPriceChart } from "@/components/charts/StockPriceChart";
import { Button } from "@/components/ui/button";
import {
  getPriceHistory,
  getQuote,
  type HistoryRange,
  type PriceHistory,
  type Quote,
} from "@/lib/api/market";
import { fmtMoney, fmtSignedPct, parseNum, signColor } from "@/lib/format";

const RANGES: HistoryRange[] = ["1d", "1w", "1m", "1y"];

export default function StockDetailPage() {
  const params = useParams<{ ticker: string }>();
  const ticker = (params.ticker ?? "").toUpperCase();

  const [range, setRange] = useState<HistoryRange>("1m");
  const [quote, setQuote] = useState<Quote | null>(null);
  const [history, setHistory] = useState<PriceHistory | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError(null);
    Promise.all([getQuote(ticker), getPriceHistory(ticker, range)])
      .then(([q, h]) => {
        if (!active) return;
        setQuote(q);
        setHistory(h);
      })
      .catch((err) => {
        if (active) {
          setError(err instanceof Error ? err.message : "Failed to load market data");
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [ticker, range]);

  const change = parseNum(quote?.change ?? null);
  const dayPct = parseNum(quote?.change_percent ?? null);

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto flex max-w-4xl flex-col gap-6">
        <div className="flex items-center justify-between border-b border-slate-200 pb-4">
          <div>
            <h1 className="text-2xl font-semibold text-slate-950">{ticker}</h1>
            <p className="text-sm text-slate-600">Price &amp; volume</p>
          </div>
          <Link href="/holdings" className="text-sm text-emerald-700 hover:underline">
            ← Back to Holdings
          </Link>
        </div>

        {error ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </p>
        ) : null}

        {quote ? (
          <div className="flex flex-wrap items-baseline gap-x-6 gap-y-2">
            <span className="text-3xl font-semibold text-slate-950">
              {fmtMoney(parseNum(quote.price))}
            </span>
            <span className={`text-sm font-medium ${signColor(dayPct)}`}>
              {change != null ? `${change >= 0 ? "+" : ""}${change.toFixed(2)}` : "—"} (
              {fmtSignedPct(dayPct)})
            </span>
            <span className="text-sm text-slate-500">
              Prev close {fmtMoney(parseNum(quote.previous_close))}
            </span>
          </div>
        ) : null}

        <div className="flex gap-2">
          {RANGES.map((r) => (
            <Button
              key={r}
              type="button"
              onClick={() => setRange(r)}
              className={range === r ? "border-emerald-600 text-emerald-700" : ""}
            >
              {r.toUpperCase()}
            </Button>
          ))}
        </div>

        {loading ? (
          <p className="text-sm text-slate-500">Loading chart…</p>
        ) : history ? (
          <StockPriceChart candles={history.candles} range={range} />
        ) : null}
      </div>
    </main>
  );
}
