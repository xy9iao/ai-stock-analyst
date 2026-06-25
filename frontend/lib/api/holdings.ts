import { apiFetch } from "./client";

/** A holding row as returned by the backend. Numeric fields are strings
 *  (Pydantic serializes Decimal as a string to preserve precision). */
export type Holding = {
  id: number;
  ticker: string;
  shares: string;
  average_cost: string;
  company_name: string | null;
  sector: string | null;
  notes: string | null;
  target_allocation: string | null;
  investment_thesis: string | null;
  created_at: string;
  updated_at: string;
};

/** The fields a client may send when creating a holding. */
export type HoldingInput = {
  ticker: string;
  shares: string;
  average_cost: string;
  company_name?: string | null;
  sector?: string | null;
  notes?: string | null;
  target_allocation?: string | null;
  investment_thesis?: string | null;
};

export function listHoldings(): Promise<Holding[]> {
  return apiFetch<Holding[]>("/api/holdings");
}

export function createHolding(data: HoldingInput): Promise<Holding> {
  return apiFetch<Holding>("/api/holdings", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function updateHolding(
  id: number,
  data: Partial<HoldingInput>,
): Promise<Holding> {
  return apiFetch<Holding>(`/api/holdings/${id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteHolding(id: number): Promise<void> {
  return apiFetch<void>(`/api/holdings/${id}`, { method: "DELETE" });
}
