import * as React from "react";

import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md border text-sm font-medium shadow-sm transition-colors focus:outline-none focus:ring-2 focus:ring-offset-1 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        // Emerald call-to-action: Add, Save, Generate, Send.
        primary:
          "border-emerald-600 bg-emerald-600 text-white hover:bg-emerald-700 focus:ring-emerald-500",
        // Neutral default — the original button look.
        secondary:
          "border-slate-300 bg-white text-slate-900 hover:bg-slate-50 focus:ring-slate-400",
        // Low-emphasis inline action: Edit, Cancel.
        ghost:
          "border-transparent bg-transparent text-slate-600 shadow-none hover:bg-slate-100 hover:text-slate-900 focus:ring-slate-400",
        // Destructive: Delete.
        danger: "border-red-600 bg-red-600 text-white hover:bg-red-700 focus:ring-red-500",
      },
      size: {
        default: "h-10 px-4",
        sm: "h-8 px-3 text-xs",
      },
    },
    defaultVariants: {
      variant: "secondary",
      size: "default",
    },
  },
);

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants>;

export function Button({ className, variant, size, type = "button", ...props }: ButtonProps) {
  return (
    <button type={type} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  );
}
