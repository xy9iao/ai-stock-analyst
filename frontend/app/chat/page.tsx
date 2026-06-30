"use client";

import { useState } from "react";

import { MarkdownReport } from "@/components/reports/MarkdownReport";
import { Button } from "@/components/ui/button";
import { sendMessage, type ChatContextOptions } from "@/lib/api/chat";

type Msg = { role: string; content: string };

const inputClass =
  "h-10 w-full rounded-md border border-slate-300 px-3 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-400";

export default function ChatPage() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [sessionId, setSessionId] = useState<number | undefined>(undefined);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [ctx, setCtx] = useState<ChatContextOptions>({});

  function toggle(key: "include_holdings" | "include_watchlist" | "include_recent_reports") {
    setCtx((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  function newChat() {
    setSessionId(undefined);
    setMessages([]);
    setError(null);
  }

  async function handleSend(event: React.FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || sending) return;
    setError(null);
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setSending(true);
    try {
      const res = await sendMessage({ message: text, session_id: sessionId, context: ctx });
      setSessionId(res.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Send failed");
    } finally {
      setSending(false);
    }
  }

  return (
    <main className="min-h-screen px-6 py-8">
      <div className="mx-auto flex max-w-3xl flex-col gap-4">
        <header className="flex items-center justify-between border-b border-slate-200 pb-4">
          <div>
            <h1 className="text-2xl font-semibold text-slate-950">Chat</h1>
            <p className="text-sm text-slate-600">Ask about your holdings, a stock, or the market.</p>
          </div>
          <Button type="button" onClick={newChat}>
            New chat
          </Button>
        </header>

        <div className="flex flex-wrap items-center gap-4 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm">
          <span className="font-medium text-slate-500">Context:</span>
          <label className="flex items-center gap-1.5 text-slate-700">
            <input type="checkbox" checked={!!ctx.include_holdings} onChange={() => toggle("include_holdings")} />
            Holdings
          </label>
          <label className="flex items-center gap-1.5 text-slate-700">
            <input type="checkbox" checked={!!ctx.include_watchlist} onChange={() => toggle("include_watchlist")} />
            Watchlist
          </label>
          <label className="flex items-center gap-1.5 text-slate-700">
            <input
              type="checkbox"
              checked={!!ctx.include_recent_reports}
              onChange={() => toggle("include_recent_reports")}
            />
            Recent reports
          </label>
          <input
            className={`${inputClass} w-36`}
            placeholder="Focus ticker"
            value={ctx.ticker ?? ""}
            onChange={(e) => setCtx((prev) => ({ ...prev, ticker: e.target.value || null }))}
          />
        </div>

        {error ? (
          <p className="rounded-md border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </p>
        ) : null}

        <div className="flex flex-col gap-3">
          {messages.length === 0 ? (
            <p className="rounded-lg border border-dashed border-slate-300 p-6 text-center text-sm text-slate-500">
              Start the conversation below. Toggle context to give the assistant your data.
            </p>
          ) : (
            messages.map((m, i) => (
              <div key={i} className={m.role === "user" ? "ml-auto max-w-[80%]" : "mr-auto max-w-[90%]"}>
                {m.role === "user" ? (
                  <div className="rounded-lg bg-emerald-600 px-4 py-2 text-sm text-white">{m.content}</div>
                ) : (
                  <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 shadow-sm">
                    <MarkdownReport markdown={m.content} />
                  </div>
                )}
              </div>
            ))
          )}
          {sending ? <p className="text-sm text-slate-500">Assistant is thinking…</p> : null}
        </div>

        <form onSubmit={handleSend} className="flex items-center gap-2">
          <input
            className={inputClass}
            placeholder="Type a message…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <Button type="submit" disabled={sending || !input.trim()}>
            Send
          </Button>
        </form>
      </div>
    </main>
  );
}
