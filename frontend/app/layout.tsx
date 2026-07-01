import type { Metadata } from "next";
import { Toaster } from "sonner";
import "./globals.css";
import { Footer } from "@/components/layout/Footer";
import { TopNav } from "@/components/layout/TopNav";
import { TooltipProvider } from "@/components/ui/tooltip";

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
        <TooltipProvider delayDuration={200}>{children}</TooltipProvider>
        <Footer />
        <Toaster richColors position="bottom-right" />
      </body>
    </html>
  );
}
