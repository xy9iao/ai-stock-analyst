"use client";

import { Activity, Database, LineChart } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { getBackendHealth, type BackendHealth } from "@/lib/api/client";

export default function DashboardPage() {
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [healthFailed, setHealthFailed] = useState(false);

  useEffect(() => {
    getBackendHealth()
      .then(setHealth)
      .catch(() => setHealthFailed(true));
  }, []);

  const healthStatus = healthFailed ? "error" : (health?.status ?? "…");
  const healthService = healthFailed
    ? "Backend is not reachable"
    : (health?.service ?? "Checking…");

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
        </header>

        <section className="grid gap-4 md:grid-cols-3">
          <Card>
            <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
              <Activity className="h-4 w-4 text-emerald-700" aria-hidden="true" />
              Backend Health
            </div>
            <Badge variant={healthFailed ? "danger" : "accent"}>{healthStatus}</Badge>
            <p className="mt-2 text-sm text-slate-500">{healthService}</p>
          </Card>

          <Card>
            <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
              <Database className="h-4 w-4 text-sky-700" aria-hidden="true" />
              Database
            </div>
            <p className="text-2xl font-semibold text-slate-950">PostgreSQL</p>
            <p className="mt-2 text-sm text-slate-500">
              Holdings, watchlist, reports, and chat are stored here.
            </p>
          </Card>

          <Card>
            <div className="mb-3 flex items-center gap-2 text-sm font-medium text-slate-700">
              <LineChart className="h-4 w-4 text-violet-700" aria-hidden="true" />
              Features
            </div>
            <p className="text-2xl font-semibold text-slate-950">MVP</p>
            <p className="mt-2 text-sm text-slate-500">
              Market data, news, AI reports, and chat are live.
            </p>
          </Card>
        </section>

        <Card className="p-6">
          <h2 className="text-lg font-semibold text-slate-950">Welcome</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            Manage your holdings and watchlist, view live prices and charts, generate
            AI research reports, and chat with an investment assistant — all from the
            navigation above.
          </p>
          <div className="mt-5 flex gap-2">
            <Link href="/reports">
              <Button type="button" variant="primary">
                Generate a report
              </Button>
            </Link>
            <Link href="/chat">
              <Button type="button">Open chat</Button>
            </Link>
          </div>
        </Card>
      </div>
    </main>
  );
}
