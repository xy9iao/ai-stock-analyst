import { apiFetch } from "./client";

export type ReportType = "single_stock" | "portfolio" | "research";

export type Report = {
  id: number;
  report_type: string;
  title: string;
  content_markdown: string;
  created_at: string;
};

export type GenerateReportInput = {
  report_type: ReportType;
  ticker?: string;
  query?: string;
};

export function generateReport(data: GenerateReportInput): Promise<Report> {
  return apiFetch<Report>("/api/reports", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function listReports(): Promise<Report[]> {
  return apiFetch<Report[]>("/api/reports");
}

export function getReport(id: number): Promise<Report> {
  return apiFetch<Report>(`/api/reports/${id}`);
}
