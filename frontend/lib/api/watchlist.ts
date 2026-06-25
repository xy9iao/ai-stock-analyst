import { apiFetch } from "./client";

/** A watchlist item as returned by the backend. */
export type WatchlistItem = {
  id: number;
  ticker: string;
  company_name: string | null;
  sector: string | null;
  reason_to_watch: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
};

/** The fields a client may send when adding a watchlist item. */
export type WatchlistItemInput = {
  ticker: string;
  company_name?: string | null;
  sector?: string | null;
  reason_to_watch?: string | null;
  notes?: string | null;
};

export function listWatchlist(): Promise<WatchlistItem[]> {
  return apiFetch<WatchlistItem[]>("/api/watchlist");
}

export function createWatchlistItem(
  data: WatchlistItemInput,
): Promise<WatchlistItem> {
  return apiFetch<WatchlistItem>("/api/watchlist", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateWatchlistItem(
  id: number,
  data: Partial<WatchlistItemInput>,
): Promise<WatchlistItem> {
  return apiFetch<WatchlistItem>(`/api/watchlist/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteWatchlistItem(id: number): Promise<void> {
  return apiFetch<void>(`/api/watchlist/${id}`, { method: "DELETE" });
}
