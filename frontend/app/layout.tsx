import type { Metadata } from "next";
import { Toaster } from "sonner";
import "./globals.css";
import { TopNav } from "@/components/layout/TopNav";

export const metadata: Metadata = {
  title: "AI Stock Analyst",
  description: "Local-first AI-powered stock research assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <TopNav />
        {children}
        <Toaster richColors position="bottom-right" />
      </body>
    </html>
  );
}
