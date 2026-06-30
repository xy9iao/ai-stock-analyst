import { Activity, Database, LineChart } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { getBackendHealth } from "@/lib/api/client";

export default async function DashboardPage() {
  let healthStatus = "unavailable";
  let healthService = "Backend is not reachable";

  try {
    const health = await getBackendHealth();
    healthStatus = health.status;
    healthService = health.service;
  } catch {
    healthStatus = "error";
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-8">
        <header className="flex flex-col gap-3 border-b border-slate-200 pb-6">
          <div className="flex items-center gap-3">
            <LineChart className="h-8 w-8 text-emerald-700" aria-hidden="true" />
            <div>
              <h1 className="text-3xl font-semibold tracking-normal text-slate-950">
                AI Stock Analyst
              </h1>
              <p className="text-sm text-slate-600">
                Local-first investment research dashboard
              </p>
            </div>
          </div>
          <nav className="flex gap-4 text-sm font-medium text-slate-700">
            <Link href="/holdings" className="hover:text-emerald-700">
              Holdings
            </Link>
            <Link href="/watchlist" className="hover:text-emerald-700">
              Watchlist
            </Link>
            <Link href="/reports" className="hover:text-emerald-700">
              Reports
            </Link>
            <Link href="/chat" className="hover:text-emerald-700">
              Chat
            </Link>
          </nav>
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
              <Activity className="h-4 w-4 text-emerald-700" aria-hidden="true" />
              Backend Health
            </div>
            <p className="text-2xl font-semibold text-slate-950">{healthStatus}</p>
            <p className="mt-2 text-sm text-slate-500">{healthService}</p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
              <Database className="h-4 w-4 text-sky-700" aria-hidden="true" />
              Database
            </div>
            <p className="text-2xl font-semibold text-slate-950">PostgreSQL</p>
            <p className="mt-2 text-sm text-slate-500">
              Docker Compose service will be added in the next checkpoint.
            </p>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
              <LineChart className="h-4 w-4 text-violet-700" aria-hidden="true" />
              Dashboard
            </div>
            <p className="text-2xl font-semibold text-slate-950">Phase 1</p>
            <p className="mt-2 text-sm text-slate-500">
              Health check only. Holdings and Watchlist come later.
            </p>
          </div>
        </section>

        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-950">Basic Dashboard</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            This first screen verifies that the Next.js frontend can render and
            reach the FastAPI backend. Future phases will add holdings,
            watchlist, market data, reports, and chat.
          </p>
          <div className="mt-5">
            <Button disabled>Health check loaded on page render</Button>
          </div>
        </section>
      </div>
    </main>
  );
}
