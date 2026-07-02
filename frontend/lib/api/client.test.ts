import { afterEach, describe, expect, it, vi } from "vitest";

import { apiFetch } from "@/lib/api/client";

function mockResponse(body: unknown, init: { ok?: boolean; status?: number } = {}): Response {
  const { ok = true, status = 200 } = init;
  return { ok, status, json: async () => body } as unknown as Response;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("apiFetch", () => {
  it("prefixes the path and parses JSON on success", async () => {
    const fetchMock = vi.fn().mockResolvedValue(mockResponse({ hello: "world" }));
    vi.stubGlobal("fetch", fetchMock);

    await expect(apiFetch("/api/x")).resolves.toEqual({ hello: "world" });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/x",
      expect.objectContaining({
        headers: expect.objectContaining({ "Content-Type": "application/json" }),
      }),
    );
  });

  it("throws the backend detail.message on a non-2xx response", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        mockResponse(
          { detail: { code: "not_found", message: "Ticker not found" } },
          { ok: false, status: 404 },
        ),
      ),
    );

    await expect(apiFetch("/api/x")).rejects.toThrow("Ticker not found");
  });

  it("falls back to a generic message when the error body has no detail", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(mockResponse("oops", { ok: false, status: 500 })),
    );

    await expect(apiFetch("/api/x")).rejects.toThrow("Request failed (500)");
  });

  it("returns undefined for 204 No Content", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(mockResponse(null, { status: 204 })));

    await expect(apiFetch("/api/x")).resolves.toBeUndefined();
  });
});
