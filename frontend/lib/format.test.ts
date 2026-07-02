import { describe, expect, it } from "vitest";

import { fmtMoney, fmtSignedPct, parseNum, signColor } from "@/lib/format";

describe("parseNum", () => {
  it("parses numeric strings", () => {
    expect(parseNum("12.5")).toBe(12.5);
    expect(parseNum("0")).toBe(0);
  });
  it("returns null for null/undefined/non-numeric", () => {
    expect(parseNum(null)).toBeNull();
    expect(parseNum(undefined)).toBeNull();
    expect(parseNum("abc")).toBeNull();
  });
});

describe("fmtMoney", () => {
  it("formats with two decimals (locale-tolerant separators)", () => {
    expect(fmtMoney(5)).toMatch(/^5[.,]00$/);
    expect(fmtMoney(1234.5)).toMatch(/^1[.,]?234[.,]50$/);
  });
  it("returns an em dash for null", () => {
    expect(fmtMoney(null)).toBe("—");
  });
});

describe("fmtSignedPct", () => {
  it("adds a + for non-negative values", () => {
    expect(fmtSignedPct(2.5)).toBe("+2.50%");
    expect(fmtSignedPct(0)).toBe("+0.00%");
  });
  it("keeps the minus sign for negatives", () => {
    expect(fmtSignedPct(-1.2)).toBe("-1.20%");
  });
  it("returns an em dash for null", () => {
    expect(fmtSignedPct(null)).toBe("—");
  });
});

describe("signColor", () => {
  it("maps sign to a tailwind text class", () => {
    expect(signColor(1)).toBe("text-emerald-700");
    expect(signColor(-1)).toBe("text-red-600");
    expect(signColor(null)).toBe("text-slate-500");
  });
});
