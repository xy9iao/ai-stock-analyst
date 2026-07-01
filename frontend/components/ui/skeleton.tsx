import * as React from "react";

import { cn } from "@/lib/utils";

// A pulsing grey placeholder shown while data loads.
export function Skeleton({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return <div className={cn("animate-pulse rounded-md bg-slate-200", className)} {...props} />;
}
