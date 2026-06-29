/** Shared display-formatting helpers for market values (rendering only). */

export function parseNum(value: string | null | undefined): number | null {
  if (value == null) return null;
  const n = Number(value);
  return Number.isFinite(n) ? n : null;
}

export function fmtMoney(n: number | null): string {
  if (n == null) return "—";
  return n.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

export function fmtSignedPct(n: number | null): string {
  if (n == null) return "—";
  return `${n >= 0 ? "+" : ""}${n.toFixed(2)}%`;
}

export function signColor(n: number | null): string {
  if (n == null) return "text-slate-500";
  return n >= 0 ? "text-emerald-700" : "text-red-600";
}
