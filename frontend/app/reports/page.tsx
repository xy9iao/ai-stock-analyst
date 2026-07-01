"use client";

import { useEffect, useState } from "react";

import { MarkdownReport } from "@/components/reports/MarkdownReport";
import { Button } from "@/components/ui/button";
import {
  generateReport,
  listReports,
  type Report,
  type ReportType,
} from "@/lib/api/reports";
import { downloadText, slugFilename } from "@/lib/download";

const inputClass =
  "h-10 w-full rounded-md border border-slate-300 px-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400";

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
    setError(null);
    try {
      const report = await generateReport({
        report_type: reportType,
        ticker: reportType === "single_stock" ? ticker : undefined,
      });
      setSelected(report);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Generation failed");
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

        {error ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </p>
        ) : null}

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
            <input
              className={`${inputClass} w-44`}
              placeholder="Ticker (e.g. NVDA)"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              required
            />
          ) : null}
          <Button type="submit" disabled={generating}>
            {generating ? "Generating… (~30s)" : "Generate report"}
          </Button>
        </form>

        {selected ? (
          <article className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
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
          </article>
        ) : null}

        <section>
          <h2 className="mb-2 text-sm font-medium text-slate-500">Past reports</h2>
          {reports.length === 0 ? (
            <p className="text-sm text-slate-500">No reports yet.</p>
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
