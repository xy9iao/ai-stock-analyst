export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/** Handled backend errors arrive as {"detail": {"code", "message"}} (see core/errors.py). */
export type ApiErrorDetail = { code: string; message: string };

/**
 * Thin wrapper around fetch for talking to the backend:
 * prefixes the base URL, sends/parses JSON, and turns any non-2xx
 * response into a thrown Error carrying the backend's message.
 */
export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });

  if (!response.ok) {
    throw new Error(await extractErrorMessage(response));
  }

  // 204 No Content (e.g. a successful DELETE) has no body to parse.
  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function extractErrorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    const detail = body?.detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail.message === "string") return detail.message;
  } catch {
    // Non-JSON error body; fall through to a generic message.
  }
  return `Request failed (${response.status})`;
}

export type BackendHealth = { status: string; service: string };

export function getBackendHealth(): Promise<BackendHealth> {
  return apiFetch<BackendHealth>("/api/health");
}
