"use client";

import { LineChart } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

// The logo links home, so the nav lists only the section pages.
const links = [
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
  return (
    <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center gap-6 px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold text-slate-950">
          <LineChart className="h-5 w-5 text-emerald-700" aria-hidden="true" />
          AI Stock Analyst
        </Link>
        <nav className="flex items-center gap-1 text-sm font-medium">
          {links.map((link) => {
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
    </header>
  );
}
