import { afterEach, describe, expect, it, vi } from "vitest";

import { createHolding, deleteHolding, listHoldings } from "@/lib/api/holdings";

function jsonResponse(body: unknown, status = 200): Response {
  return { ok: true, status, json: async () => body } as unknown as Response;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("holdings api", () => {
  it("listHoldings GETs /api/holdings", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse([]));
    vi.stubGlobal("fetch", fetchMock);

    await listHoldings();
    expect(fetchMock).toHaveBeenCalledWith("/api/holdings", expect.any(Object));
  });

  it("createHolding POSTs the payload as JSON", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ id: 1 }));
    vi.stubGlobal("fetch", fetchMock);

    const input = { ticker: "NVDA", shares: "1", average_cost: "10" };
    await createHolding(input);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/holdings",
      expect.objectContaining({ method: "POST", body: JSON.stringify(input) }),
    );
  });

  it("deleteHolding sends DELETE and resolves undefined on 204", async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse(null, 204));
    vi.stubGlobal("fetch", fetchMock);

    await expect(deleteHolding(5)).resolves.toBeUndefined();
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/holdings/5",
      expect.objectContaining({ method: "DELETE" }),
    );
  });
});
