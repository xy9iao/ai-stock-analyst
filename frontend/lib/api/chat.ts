import { apiFetch } from "./client";

export type ChatContextOptions = {
  include_holdings?: boolean;
  include_watchlist?: boolean;
  ticker?: string | null;
  include_recent_reports?: boolean;
};

export type ChatReply = {
  session_id: number;
  reply: string;
};

export type ChatMessage = {
  id: number;
  role: string;
  content: string;
  created_at: string;
};

export type ChatSession = {
  id: number;
  title: string | null;
  created_at: string;
};

export type SendMessageInput = {
  message: string;
  session_id?: number;
  context?: ChatContextOptions;
};

export function sendMessage(input: SendMessageInput): Promise<ChatReply> {
  return apiFetch<ChatReply>("/api/chat/messages", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function listSessions(): Promise<ChatSession[]> {
  return apiFetch<ChatSession[]>("/api/chat/sessions");
}

export function getSessionMessages(sessionId: number): Promise<ChatMessage[]> {
  return apiFetch<ChatMessage[]>(`/api/chat/sessions/${sessionId}/messages`);
}
