type MarkdownReportProps = {
  markdown: string;
};

export function MarkdownReport({ markdown }: MarkdownReportProps) {
  return (
    <pre className="whitespace-pre-wrap rounded-md border border-slate-200 bg-white p-4 text-sm text-slate-700">
      {markdown}
    </pre>
  );
}
