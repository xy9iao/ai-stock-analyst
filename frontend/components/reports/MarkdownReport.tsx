"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export function MarkdownReport({ markdown }: { markdown: string }) {
  return (
    <div className="prose prose-slate max-w-none prose-headings:font-semibold prose-h1:text-2xl prose-h2:text-lg">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{markdown}</ReactMarkdown>
    </div>
  );
}
