"use client";

import { resetSession } from "@/lib/api/session";

export function Footer() {
  async function handleReset() {
    try {
      await resetSession();
    } finally {
      // Reload so every page refetches under the fresh (empty) session.
      window.location.href = "/";
    }
  }

  return (
    <footer className="border-t border-slate-200 px-6 py-4 text-center text-xs text-slate-500">
      <p>
        For research and educational use only — not financial advice. Market data may be delayed
        or inaccurate; verify independently before making decisions.
      </p>
      <button
        type="button"
        onClick={handleReset}
        className="mt-1 underline decoration-slate-300 underline-offset-2 hover:text-slate-700"
      >
        New demo session
      </button>
    </footer>
  );
}
