import * as React from "react";

import { cn } from "@/lib/utils";

// The repeated surface used across pages: white panel, subtle border + shadow.
// Pages can override padding etc. via className.
export function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("rounded-lg border border-slate-200 bg-white p-5 shadow-sm", className)}
      {...props}
    />
  );
}
