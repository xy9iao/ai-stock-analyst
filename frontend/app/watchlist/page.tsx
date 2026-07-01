"use client";

import { useEffect, useState } from "react";

import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getQuote, type Quote } from "@/lib/api/market";
import {
  createWatchlistItem,
  deleteWatchlistItem,
  listWatchlist,
  updateWatchlistItem,
  type WatchlistItem,
  type WatchlistItemInput,
} from "@/lib/api/watchlist";
import { fmtMoney, fmtSignedPct, parseNum, signColor } from "@/lib/format";

const EMPTY_FORM: WatchlistItemInput = {
  ticker: "",
  company_name: "",
  sector: "",
  reason_to_watch: "",
};

export default function WatchlistPage() {
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [quotes, setQuotes] = useState<Record<string, Quote | undefined>>({});
  const [quotesLoading, setQuotesLoading] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<WatchlistItemInput>(EMPTY_FORM);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function loadQuotes(rows: WatchlistItem[]) {
    setQuotesLoading(true);
    try {
      const entries = await Promise.all(
        rows.map(async (item): Promise<[string, Quote | undefined]> => {
          try {
            return [item.ticker, await getQuote(item.ticker)];
          } catch {
            return [item.ticker, undefined];
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
      const data = await listWatchlist();
      setItems(data);
      void loadQuotes(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load watchlist");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- load once on mount
  }, []);

  function setField(field: keyof WatchlistItemInput, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  function startEdit(item: WatchlistItem) {
    setEditingId(item.id);
    setForm({
      ticker: item.ticker,
      company_name: item.company_name ?? "",
      sector: item.sector ?? "",
      reason_to_watch: item.reason_to_watch ?? "",
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
        await createWatchlistItem(form);
      } else {
        await updateWatchlistItem(editingId, form);
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
      await deleteWatchlistItem(id);
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
          <h1 className="text-2xl font-semibold text-slate-950">Watchlist</h1>
          <p className="text-sm text-slate-600">Stocks you are keeping an eye on.</p>
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
          <Input
            placeholder="Ticker (e.g. NVDA)"
            value={form.ticker}
            onChange={(e) => setField("ticker", e.target.value)}
            required
          />
          <Input
            placeholder="Company name (optional)"
            value={form.company_name ?? ""}
            onChange={(e) => setField("company_name", e.target.value)}
          />
          <Input
            placeholder="Sector (optional)"
            value={form.sector ?? ""}
            onChange={(e) => setField("sector", e.target.value)}
          />
          <Input
            placeholder="Reason to watch (optional)"
            value={form.reason_to_watch ?? ""}
            onChange={(e) => setField("reason_to_watch", e.target.value)}
          />
          <div className="flex items-center gap-2">
            <Button type="submit" variant="primary" disabled={submitting}>
              {editingId === null ? "Add to watchlist" : "Save changes"}
            </Button>
            {editingId !== null ? (
              <Button type="button" variant="ghost" onClick={cancelEdit}>
                Cancel
              </Button>
            ) : null}
          </div>
        </form>

        {loading ? (
          <p className="text-sm text-slate-500">Loading watchlist…</p>
        ) : items.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
            Nothing on your watchlist yet. Add a ticker above.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-slate-200 bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Ticker</th>
                  <th className="px-4 py-3 font-medium">Company</th>
                  <th className="px-4 py-3 font-medium">Sector</th>
                  <th className="px-4 py-3 font-medium">Reason to watch</th>
                  <th className="px-4 py-3 font-medium">Price</th>
                  <th className="px-4 py-3 font-medium">Day %</th>
                  <th className="px-4 py-3 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => {
                  const quote = quotes[item.ticker];
                  const dayPct = parseNum(quote?.change_percent);
                  return (
                    <tr key={item.id} className="border-b border-slate-100 last:border-0">
                      <td className="px-4 py-3 font-medium">
                        <Link
                          href={`/stocks/${item.ticker}`}
                          className="text-emerald-700 hover:underline"
                        >
                          {item.ticker}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-slate-600">{item.company_name ?? "—"}</td>
                      <td className="px-4 py-3 text-slate-600">{item.sector ?? "—"}</td>
                      <td className="px-4 py-3 text-slate-600">{item.reason_to_watch ?? "—"}</td>
                      <td className="px-4 py-3 text-slate-600">
                        {marketCell(quote ? fmtMoney(parseNum(quote.price)) : "—")}
                      </td>
                      <td className={`px-4 py-3 ${signColor(dayPct)}`}>
                        {marketCell(fmtSignedPct(dayPct))}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex justify-end gap-2">
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            onClick={() => startEdit(item)}
                          >
                            Edit
                          </Button>
                          <Button
                            type="button"
                            variant="danger"
                            size="sm"
                            onClick={() => handleDelete(item.id)}
                          >
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
