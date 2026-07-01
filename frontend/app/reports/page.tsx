"use client";

import { useEffect, useState } from "react";

import { toast } from "sonner";

import { MarkdownReport } from "@/components/reports/MarkdownReport";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import {
  generateReport,
  listReports,
  type Report,
  type ReportType,
} from "@/lib/api/reports";
import { downloadText, slugFilename } from "@/lib/download";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [selected, setSelected] = useState<Report | null>(null);
  const [reportType, setReportType] = useState<ReportType>("single_stock");
  const [ticker, setTicker] = useState("");
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    try {
      setReports(await listReports());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load reports");
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleGenerate(event: React.FormEvent) {
    event.preventDefault();
    setGenerating(true);
    try {
      const report = await generateReport({
        report_type: reportType,
        ticker: reportType === "single_stock" ? ticker : undefined,
      });
      setSelected(report);
      await refresh();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Generation failed");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <header className="border-b border-slate-200 pb-4">
          <h1 className="text-2xl font-semibold text-slate-950">AI Reports</h1>
          <p className="text-sm text-slate-600">Generate an AI research report.</p>
        </header>

        <form
          onSubmit={handleGenerate}
          className="flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
        >
          <Button
            type="button"
            onClick={() => setReportType("single_stock")}
            className={reportType === "single_stock" ? "border-emerald-600 text-emerald-700" : ""}
          >
            Single stock
          </Button>
          <Button
            type="button"
            onClick={() => setReportType("portfolio")}
            className={reportType === "portfolio" ? "border-emerald-600 text-emerald-700" : ""}
          >
            Portfolio
          </Button>
          {reportType === "single_stock" ? (
            <Input
              className="w-44"
              placeholder="Ticker (e.g. NVDA)"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              required
            />
          ) : null}
          <Button type="submit" variant="primary" disabled={generating}>
            {generating ? "Generating… (~30s)" : "Generate report"}
          </Button>
        </form>

        {generating ? (
          <Card className="p-6">
            <div className="space-y-3">
              <Skeleton className="h-6 w-2/3" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-5/6" />
            </div>
          </Card>
        ) : selected ? (
          <Card className="p-6">
            <div className="mb-4 flex justify-end">
              <Button
                type="button"
                onClick={() =>
                  downloadText(slugFilename(selected.title), selected.content_markdown)
                }
              >
                Download .md
              </Button>
            </div>
            <MarkdownReport markdown={selected.content_markdown} />
          </Card>
        ) : null}

        <section>
          <h2 className="mb-2 text-sm font-medium text-slate-500">Past reports</h2>
          {error ? (
            <EmptyState title="Couldn't load reports" description={error} />
          ) : reports.length === 0 ? (
            <EmptyState title="No reports yet" description="Generate your first report above." />
          ) : (
            <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white shadow-sm">
              {reports.map((report) => (
                <li key={report.id}>
                  <button
                    type="button"
                    onClick={() => setSelected(report)}
                    className="flex w-full items-center justify-between gap-4 px-4 py-3 text-left text-sm hover:bg-slate-50"
                  >
                    <span className="font-medium text-slate-900">{report.title}</span>
                    <span className="shrink-0 text-slate-400">
                      {new Date(report.created_at).toLocaleString()}
                    </span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
