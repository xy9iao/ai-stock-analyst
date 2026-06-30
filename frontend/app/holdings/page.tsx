"use client";

import { useEffect, useState } from "react";

import Link from "next/link";

import { Button } from "@/components/ui/button";
import {
  createHolding,
  deleteHolding,
  listHoldings,
  updateHolding,
  type Holding,
  type HoldingInput,
} from "@/lib/api/holdings";
import { getQuote, type Quote } from "@/lib/api/market";
import { fmtMoney, fmtSignedPct, parseNum, signColor } from "@/lib/format";

const EMPTY_FORM: HoldingInput = {
  ticker: "",
  shares: "",
  average_cost: "",
  company_name: "",
  sector: "",
};

const inputClass =
  "h-10 w-full rounded-md border border-slate-300 px-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400";

// Display-only math: parse the Decimal strings to numbers just for rendering.
// The backend stays the source of truth.
function marketValue(holding: Holding, quote: Quote | undefined): number | null {
  const shares = parseNum(holding.shares);
  const price = parseNum(quote?.price);
  if (shares == null || price == null) return null;
  return shares * price;
}

function gainLossPct(holding: Holding, quote: Quote | undefined): number | null {
  const shares = parseNum(holding.shares);
  const price = parseNum(quote?.price);
  const cost = parseNum(holding.average_cost);
  if (shares == null || price == null || cost == null || cost === 0) return null;
  const value = shares * price;
  const basis = shares * cost;
  return ((value - basis) / basis) * 100;
}

export default function HoldingsPage() {
  const [holdings, setHoldings] = useState<Holding[]>([]);
  const [quotes, setQuotes] = useState<Record<string, Quote | undefined>>({});
  const [quotesLoading, setQuotesLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<HoldingInput>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function loadQuotes(rows: Holding[]) {
    setQuotesLoading(true);
    try {
      const entries = await Promise.all(
        rows.map(async (h): Promise<[string, Quote | undefined]> => {
          try {
            return [h.ticker, await getQuote(h.ticker)];
          } catch {
            return [h.ticker, undefined];
          }
        }),
      );
      setQuotes(Object.fromEntries(entries));
    } finally {
      setQuotesLoading(false);
    }
  }

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const data = await listHoldings();
      setHoldings(data);
      void loadQuotes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load holdings");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- load once on mount
  }, []);

  function setField(field: keyof HoldingInput, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function startEdit(holding: Holding) {
    setEditingId(holding.id);
    setForm({
      ticker: holding.ticker,
      shares: holding.shares,
      average_cost: holding.average_cost,
      company_name: holding.company_name ?? "",
      sector: holding.sector ?? "",
    });
  }

  function cancelEdit() {
    setEditingId(null);
    setForm(EMPTY_FORM);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      if (editingId === null) {
        await createHolding(form);
      } else {
        await updateHolding(editingId, form);
      }
      cancelEdit();
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id: number) {
    setError(null);
    try {
      await deleteHolding(id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Delete failed");
    }
  }

  function marketCell(value: string) {
    return quotesLoading ? "…" : value;
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-6">
        <header className="border-b border-slate-200 pb-4">
          <h1 className="text-2xl font-semibold text-slate-950">Holdings</h1>
          <p className="text-sm text-slate-600">Stocks you currently own.</p>
        </header>

        {error ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </p>
        ) : null}

        <form
          onSubmit={handleSubmit}
          className="grid gap-3 rounded-lg border border-slate-200 bg-white p-5 shadow-sm sm:grid-cols-2"
        >
          <input
            className={inputClass}
            placeholder="Ticker (e.g. NVDA)"
            value={form.ticker}
            onChange={(e) => setField("ticker", e.target.value)}
            required
          />
          <input
            className={inputClass}
            placeholder="Company name (optional)"
            value={form.company_name ?? ""}
            onChange={(e) => setField("company_name", e.target.value)}
          />
          <input
            className={inputClass}
            placeholder="Shares"
            value={form.shares}
            onChange={(e) => setField("shares", e.target.value)}
            required
          />
          <input
            className={inputClass}
            placeholder="Average cost"
            value={form.average_cost}
            onChange={(e) => setField("average_cost", e.target.value)}
            required
          />
          <input
            className={inputClass}
            placeholder="Sector (optional)"
            value={form.sector ?? ""}
            onChange={(e) => setField("sector", e.target.value)}
          />
          <div className="flex items-center gap-2">
            <Button type="submit" disabled={submitting}>
              {editingId === null ? "Add holding" : "Save changes"}
            </Button>
            {editingId !== null ? (
              <Button type="button" onClick={cancelEdit}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>

        {loading ? (
          <p className="text-sm text-slate-500">Loading holdings…</p>
        ) : holdings.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
            No holdings yet. Add your first one above.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Ticker</th>
                  <th className="px-4 py-3 font-medium">Company</th>
                  <th className="px-4 py-3 font-medium">Shares</th>
                  <th className="px-4 py-3 font-medium">Avg cost</th>
                  <th className="px-4 py-3 font-medium">Price</th>
                  <th className="px-4 py-3 font-medium">Day %</th>
                  <th className="px-4 py-3 font-medium">Value</th>
                  <th className="px-4 py-3 font-medium">Gain/Loss</th>
                  <th className="px-4 py-3 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding) => {
                  const quote = quotes[holding.ticker];
                  const dayPct = parseNum(quote?.change_percent);
                  const glPct = gainLossPct(holding, quote);
                  return (
                    <tr key={holding.id} className="border-b border-slate-100 last:border-0">
                      <td className="px-4 py-3 font-medium">
                        <Link
                          href={`/stocks/${holding.ticker}`}
                          className="text-emerald-700 hover:underline"
                        >
                          {holding.ticker}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-slate-600">{holding.company_name ?? "—"}</td>
                      <td className="px-4 py-3 text-slate-600">{holding.shares}</td>
                      <td className="px-4 py-3 text-slate-600">{holding.average_cost}</td>
                      <td className="px-4 py-3 text-slate-600">
                        {marketCell(quote ? fmtMoney(parseNum(quote.price)) : "—")}
                      </td>
                      <td className={`px-4 py-3 ${signColor(dayPct)}`}>
                        {marketCell(fmtSignedPct(dayPct))}
                      </td>
                      <td className="px-4 py-3 text-slate-600">
                        {marketCell(fmtMoney(marketValue(holding, quote)))}
                      </td>
                      <td className={`px-4 py-3 ${signColor(glPct)}`}>
                        {marketCell(fmtSignedPct(glPct))}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex justify-end gap-2">
                          <Button type="button" onClick={() => startEdit(holding)}>
                            Edit
                          </Button>
                          <Button type="button" onClick={() => handleDelete(holding.id)}>
                            Delete
                          </Button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
