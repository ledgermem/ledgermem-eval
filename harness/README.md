# Harness

The Python evaluation harness lives in `src/ledgermem_eval/`. This directory
holds harness-specific docs, datasets, and reproducibility artefacts.

## Quick start

```bash
pip install -e ".[dev]"
ledgermem-eval list-benchmarks
ledgermem-eval list-systems
ledgermem-eval run --benchmark longmemeval --mock --output ./results
```

## Adding a new benchmark

1. Create `src/ledgermem_eval/benchmarks/my_bench.py` exporting a class that
   subclasses `Benchmark` and implements `load_suite()`.
2. Register it in `src/ledgermem_eval/benchmarks/__init__.py`.
3. Add a fixture-only smoke test under `tests/`.

## Adding a new adapter

1. Create `src/ledgermem_eval/adapters/<system>_adapter.py` subclassing
   `Adapter`.
2. Implement `setup`, `teardown`, `load_episodes`, `add`, `search`.
3. Register it in `src/ledgermem_eval/adapters/__init__.py`.

## Reproducibility

All published numbers come from running:

```bash
docker build -t ledgermem-eval .
docker run --rm \
    -e LEDGERMEM_API_KEY=... \
    -e LEDGERMEM_WORKSPACE_ID=... \
    -v "$PWD/results:/work/results" \
    ledgermem-eval run --benchmark longmemeval --systems all --output /work/results
```

The `git_sha` of this repo is captured into every results JSON file so any
result can be reproduced from the matching commit.
