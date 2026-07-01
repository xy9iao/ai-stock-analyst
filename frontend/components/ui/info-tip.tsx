"use client";

import type { ReactNode } from "react";

import { Info } from "lucide-react";

import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

// A label paired with an info icon that explains a finance term on hover/focus.
// Used on table column headers to make the app friendlier for beginners.
export function InfoTip({ label, children }: { label: string; children: ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1">
      {label}
      <Tooltip>
        <TooltipTrigger asChild>
          <button
            type="button"
            aria-label={`What is ${label}?`}
            className="rounded text-slate-400 hover:text-slate-600 focus:outline-none focus:ring-2 focus:ring-slate-400"
          >
            <Info className="h-3.5 w-3.5" aria-hidden="true" />
          </button>
        </TooltipTrigger>
        <TooltipContent>{children}</TooltipContent>
      </Tooltip>
    </span>
  );
}
