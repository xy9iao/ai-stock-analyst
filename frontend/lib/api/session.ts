import { apiFetch } from "./client";

/** Drop the demo-session cookie; the next request starts a fresh, empty bucket. */
export function resetSession(): Promise<void> {
  return apiFetch<void>("/api/session/reset", { method: "POST" });
}
