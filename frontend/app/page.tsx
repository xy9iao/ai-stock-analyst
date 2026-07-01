import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

export default function HomePage() {
  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto flex max-w-6xl flex-col gap-8">
        <Card className="p-6">
          <h1 className="text-2xl font-semibold text-slate-950">Welcome to AI Stock Analyst</h1>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            A local-first assistant for stock research — track your holdings and watchlist, view
            live prices and charts, generate AI research reports, and chat with an investment
            assistant. Use the navigation above to get started.
          </p>
          <div className="mt-5 flex gap-2">
            <Link href="/reports">
              <Button variant="primary">Generate a report</Button>
            </Link>
            <Link href="/chat">
              <Button>Open chat</Button>
            </Link>
          </div>
        </Card>
      </div>
    </main>
  );
}
