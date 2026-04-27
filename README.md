# ledgermem-eval

Open-source benchmark harness and public leaderboard for LLM memory systems.

This repo contains two complementary parts:

- **`src/`, `tests/`, `harness/`** — a Python harness that runs a set of
  reproducible benchmarks (LongMemEval, LoCoMo, RealAgentMem) against a
  pluggable set of memory systems (LedgerMem, Mem0, Zep, OpenAI Assistants,
  baseline).
- **`web/`** — a Next.js leaderboard at
  [eval.proofly.dev](https://eval.proofly.dev) that pulls published runs from
  a public R2 bucket and renders sortable tables and Pareto charts.

## Why another benchmark?

Memory benchmarks for LLM agents are still young, and most published numbers
are produced by the system's own authors with no third-party reproduction. We
care about three properties:

1. **Reproducibility.** Pin the harness, pin the model, pin the dataset.
2. **Latency honesty.** Cloud systems do not get to strip the network.
3. **Open submissions.** Any new memory system can land an adapter via PR.

## Quick reproduction

```bash
docker pull ledgermem/eval:latest
docker run --rm \
  -e LEDGERMEM_API_KEY=... \
  -e LEDGERMEM_WORKSPACE_ID=... \
  -e MEM0_API_KEY=... \
  -e ZEP_API_KEY=... \
  -e OPENAI_API_KEY=... \
  -v "$PWD/results:/work/results" \
  ledgermem/eval run --benchmark longmemeval --systems all --output /work/results
```

Or, using the harness directly:

```bash
pip install -e ".[dev]"
ledgermem-eval list-benchmarks
ledgermem-eval run --benchmark longmemeval --mock --output ./results
```

## Layout

```
.
├── src/ledgermem_eval/        # Python harness
│   ├── adapters/              # one file per memory system
│   ├── benchmarks/            # one file per benchmark
│   ├── scoring.py             # recall, precision, F1, latency percentiles
│   ├── output.py              # JSON result serialization
│   └── cli.py                 # ledgermem-eval CLI (click)
├── tests/                     # pytest unit + smoke tests
├── harness/                   # docs and reproducibility artefacts
├── web/                       # Next.js leaderboard site
├── Dockerfile                 # pinned image for reproducible runs
└── .github/workflows/         # CI + scheduled bench runs
```

## Submitting a system

1. Add `src/ledgermem_eval/adapters/<name>_adapter.py` subclassing `Adapter`.
2. Register it in `src/ledgermem_eval/adapters/__init__.py`.
3. Open a PR — CI will smoke-test the adapter against the bundled fixtures.

See `harness/README.md` for the full submission guide and the rules in
`web/app/methodology/page.tsx`.

## License

Apache 2.0 for code, CC-BY 4.0 for benchmark fixtures and prose.
