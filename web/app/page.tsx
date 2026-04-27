export default function HomePage() {
  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-4xl font-bold tracking-tight">
          Open benchmarks for LLM memory systems
        </h1>
        <p className="mt-4 max-w-2xl text-neutral-600">
          LedgerMem Eval is a reproducible harness that compares memory systems
          across LongMemEval, LoCoMo, and our own RealAgentMem suite. Every
          number on this site can be regenerated from the
          <a
            href="https://github.com/ledgermem/ledgermem-eval"
            className="underline"
          >
            {" "}
            open-source harness
          </a>
          .
        </p>
      </section>

      <section className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <a
          href="/leaderboard"
          className="rounded-lg border border-neutral-200 p-6 transition hover:border-neutral-400"
        >
          <h2 className="text-lg font-semibold">Leaderboard</h2>
          <p className="mt-2 text-sm text-neutral-600">
            Sortable tables across systems and benchmarks. Recall, precision,
            F1, p50/p95 latency.
          </p>
        </a>
        <a
          href="/methodology"
          className="rounded-lg border border-neutral-200 p-6 transition hover:border-neutral-400"
        >
          <h2 className="text-lg font-semibold">Methodology</h2>
          <p className="mt-2 text-sm text-neutral-600">
            Anti-bias rules, scoring definitions, and how we keep the harness
            honest.
          </p>
        </a>
        <a
          href="https://github.com/ledgermem/ledgermem-eval"
          className="rounded-lg border border-neutral-200 p-6 transition hover:border-neutral-400"
        >
          <h2 className="text-lg font-semibold">Reproduce</h2>
          <p className="mt-2 text-sm text-neutral-600">
            <code className="rounded bg-neutral-100 px-1 text-xs">
              docker run ledgermem/eval
            </code>{" "}
            and you have the same numbers.
          </p>
        </a>
      </section>
    </div>
  );
}
