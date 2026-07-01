"use client";

import { useState } from "react";

import { toast } from "sonner";

import { MarkdownReport } from "@/components/reports/MarkdownReport";
import { Button } from "@/components/ui/button";
import { EmptyState } from "@/components/ui/empty-state";
import { InfoTip } from "@/components/ui/info-tip";
import { Input } from "@/components/ui/input";
import { sendMessage, type ChatContextOptions } from "@/lib/api/chat";
import { downloadText } from "@/lib/download";

type Msg = { role: string; content: string };

function chatToMarkdown(messages: Msg[]): string {
  const lines = ["# Chat transcript", ""];
  for (const m of messages) {
    lines.push(m.role === "user" ? "**You:**" : "**Assistant:**", "", m.content, "");
  }
  return lines.join("\n");
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [sessionId, setSessionId] = useState<number | undefined>(undefined);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [ctx, setCtx] = useState<ChatContextOptions>({});

  function toggle(key: "include_holdings" | "include_watchlist" | "include_recent_reports") {
    setCtx((prev) => ({ ...prev, [key]: !prev[key] }));
  }

  function newChat() {
    setSessionId(undefined);
    setMessages([]);
  }

  async function handleSend(event: React.FormEvent) {
    event.preventDefault();
    const text = input.trim();
    if (!text || sending) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setSending(true);
    try {
      const res = await sendMessage({ message: text, session_id: sessionId, context: ctx });
      setSessionId(res.session_id);
      setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Send failed");
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
          <div className="flex gap-2">
            <Button
              type="button"
              onClick={() => downloadText("chat.md", chatToMarkdown(messages))}
              disabled={messages.length === 0}
            >
              Export
            </Button>
            <Button type="button" onClick={newChat}>
              New chat
            </Button>
          </div>
        </header>

        <div className="flex flex-wrap items-center gap-4 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm shadow-sm">
          <span className="font-medium text-slate-500">
            <InfoTip label="Context">
              Pick which of your data the assistant can see when answering.
            </InfoTip>
          </span>
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
          <Input
            className="w-36"
            placeholder="Focus ticker"
            value={ctx.ticker ?? ""}
            onChange={(e) => setCtx((prev) => ({ ...prev, ticker: e.target.value || null }))}
          />
        </div>

        <div className="flex flex-col gap-3">
          {messages.length === 0 ? (
            <EmptyState
              title="No messages yet"
              description="Start the conversation below. Toggle context to give the assistant your data."
            />
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
          <Input
            placeholder="Type a message…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <Button type="submit" variant="primary" disabled={sending || !input.trim()}>
            Send
          </Button>
        </form>
      </div>
    </main>
  );
}
