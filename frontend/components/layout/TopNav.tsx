"use client";

import { useState } from "react";

import { ChevronDown, LineChart } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/holdings", label: "Holdings" },
  { href: "/watchlist", label: "Watchlist" },
  { href: "/reports", label: "Reports" },
  { href: "/chat", label: "Chat" },
];

// A link is active on its exact path, and (for section pages) on nested routes
// like /stocks/NVDA — but "/" only matches the dashboard itself, never everything.
function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function TopNav() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-6">
        {/* Desktop: the logo links home. */}
        <Link href="/" className="hidden items-center gap-2 font-semibold text-slate-950 md:flex">
          <LineChart className="h-5 w-5 text-emerald-700" aria-hidden="true" />
          AI Stock Analyst
        </Link>

        {/* Mobile: the logo toggles the menu. */}
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          aria-label="Toggle navigation menu"
          className="flex items-center gap-2 font-semibold text-slate-950 md:hidden"
        >
          <LineChart className="h-5 w-5 text-emerald-700" aria-hidden="true" />
          AI Stock Analyst
          <ChevronDown
            className={cn("h-4 w-4 text-slate-400 transition-transform", open && "rotate-180")}
            aria-hidden="true"
          />
        </button>

        {/* Desktop: inline section links. */}
        <nav className="hidden items-center gap-1 text-sm font-medium md:flex">
          {links.slice(1).map((link) => {
            const active = isActive(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                aria-current={active ? "page" : undefined}
                className={
                  active
                    ? "rounded-md bg-emerald-50 px-3 py-1.5 text-emerald-700"
                    : "rounded-md px-3 py-1.5 text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Mobile: dropdown menu revealed by tapping the logo. */}
      {open ? (
        <nav className="border-t border-slate-200 bg-white px-4 py-2 md:hidden">
          <ul className="flex flex-col gap-0.5">
            {links.map((link) => {
              const active = isActive(pathname, link.href);
              return (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    onClick={() => setOpen(false)}
                    aria-current={active ? "page" : undefined}
                    className={cn(
                      "block rounded-md px-3 py-2 text-sm font-medium",
                      active
                        ? "bg-emerald-50 text-emerald-700"
                        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
                    )}
                  >
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      ) : null}
    </header>
  );
}
