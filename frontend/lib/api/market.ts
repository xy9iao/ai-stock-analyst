import { apiFetch } from "./client";

export type HistoryRange = "1d" | "1w" | "1m" | "1y";

/** Current quote. Price fields are strings (backend serializes Decimal as a string). */
export type Quote = {
  ticker: string;
  price: string;
  change: string;
  change_percent: string;
  previous_close: string;
  open: string | null;
  day_high: string | null;
  day_low: string | null;
  volume: number | null;
  as_of: string | null;
};

export type Candle = {
  timestamp: string;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: number;
};

export type PriceHistory = {
  ticker: string;
  range: HistoryRange;
  candles: Candle[];
};

export function getQuote(ticker: string): Promise<Quote> {
  return apiFetch<Quote>(`/api/market/quote/${encodeURIComponent(ticker)}`);
}

export function getPriceHistory(
  ticker: string,
  range: HistoryRange,
): Promise<PriceHistory> {
  return apiFetch<PriceHistory>(
    `/api/market/history/${encodeURIComponent(ticker)}?range=${range}`,
  );
}
