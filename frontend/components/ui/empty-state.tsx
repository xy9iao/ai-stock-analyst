import * as React from "react";

import { cn } from "@/lib/utils";

type EmptyStateProps = {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  className?: string;
};

// Centered placeholder for "nothing here yet" and "couldn't load" content states.
export function EmptyState({ title, description, icon, className }: EmptyStateProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center gap-2 rounded-lg border border-dashed border-slate-300 p-10 text-center",
        className,
      )}
    >
      {icon ? <div className="text-slate-400">{icon}</div> : null}
      <p className="text-sm font-medium text-slate-900">{title}</p>
      {description ? <p className="max-w-sm text-sm text-slate-500">{description}</p> : null}
    </div>
  );
}
