import type { Metadata } from "next";
import type { ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Mnemo Eval — Open Memory Benchmarks",
  description:
    "Reproducible benchmarks comparing memory systems across LongMemEval, LoCoMo, and RealAgentMem.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-white text-neutral-900 antialiased">
        <header className="border-b border-neutral-200">
          <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
            <a href="/" className="text-lg font-semibold">
              Mnemo Eval
            </a>
            <nav className="flex gap-6 text-sm">
              <a href="/leaderboard">Leaderboard</a>
              <a href="/methodology">Methodology</a>
              <a href="https://github.com/getmnemo/getmnemo-eval">GitHub</a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-5xl px-6 py-10">{children}</main>
        <footer className="border-t border-neutral-200">
          <div className="mx-auto max-w-5xl px-6 py-6 text-sm text-neutral-500">
            Apache 2.0 — built by the Mnemo team. All numbers are
            reproducible from the harness.
          </div>
        </footer>
      </body>
    </html>
  );
}
