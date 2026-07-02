import { render, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import HoldingsPage from "@/app/holdings/page";
import { TooltipProvider } from "@/components/ui/tooltip";
import { listHoldings } from "@/lib/api/holdings";

// The page pulls holdings + quotes from these modules; auto-mock both.
vi.mock("@/lib/api/holdings");
vi.mock("@/lib/api/market");
// next/link needs the app router in tests; a passthrough is enough here.
vi.mock("next/link", () => ({
  default: ({ children }: { children: ReactNode }) => <>{children}</>,
}));

const mockList = vi.mocked(listHoldings);

// The table headers use InfoTip (radix Tooltip), which requires a provider —
// the real app mounts one in layout.tsx.
function renderPage() {
  return render(
    <TooltipProvider>
      <HoldingsPage />
    </TooltipProvider>,
  );
}

const holding = {
  id: 1,
  ticker: "NVDA",
  shares: "10",
  average_cost: "100",
  company_name: "NVIDIA",
  sector: null,
  notes: null,
  target_allocation: null,
  investment_thesis: null,
  created_at: "",
  updated_at: "",
};

afterEach(() => {
  vi.clearAllMocks();
});

describe("HoldingsPage data states", () => {
  it("shows an empty state when there are no holdings", async () => {
    mockList.mockResolvedValue([]);
    renderPage();
    expect(await screen.findByText("No holdings yet")).toBeInTheDocument();
  });

  it("renders rows when the API returns holdings", async () => {
    mockList.mockResolvedValue([holding]);
    renderPage();
    expect(await screen.findByText("NVDA")).toBeInTheDocument();
    expect(screen.getByText("NVIDIA")).toBeInTheDocument();
  });

  it("shows an error state when the API rejects", async () => {
    mockList.mockRejectedValue(new Error("boom"));
    renderPage();
    expect(await screen.findByText("Couldn't load holdings")).toBeInTheDocument();
  });
});
