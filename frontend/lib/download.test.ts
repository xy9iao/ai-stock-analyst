import { describe, expect, it } from "vitest";

import { slugFilename } from "@/lib/download";

describe("slugFilename", () => {
  it("slugifies a title with the default md extension", () => {
    expect(slugFilename("NVDA — Single-Stock Report")).toBe("nvda-single-stock-report.md");
  });
  it("collapses non-alphanumerics and trims edge dashes", () => {
    expect(slugFilename("  Hello,  World!  ")).toBe("hello-world.md");
  });
  it("honors a custom extension", () => {
    expect(slugFilename("Report", "txt")).toBe("report.txt");
  });
  it("falls back to 'export' when nothing usable remains", () => {
    expect(slugFilename("!!!")).toBe("export.md");
  });
});
