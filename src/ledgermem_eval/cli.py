"""Command-line interface for the LedgerMem evaluation harness."""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from ledgermem_eval.adapters import build_adapter, list_adapters
from ledgermem_eval.benchmarks import build_benchmark, list_benchmarks
from ledgermem_eval.output import write_results
from ledgermem_eval.scoring import score_run

console = Console()

# Default seed makes leaderboard rankings reproducible across hosts. Adapters
# and benchmark fixtures may sample from `random` (e.g. baseline retrieval),
# and without seeding, two runs of the same (system, benchmark) pair can
# produce different retrieved_ids and therefore different recall/precision —
# which then reorders the leaderboard non-deterministically. Override via
# LEDGERMEM_EVAL_SEED if you explicitly want stochastic runs.
DEFAULT_EVAL_SEED = 1337


@click.group()
@click.version_option()
def cli() -> None:
    """ledgermem-eval — run memory benchmarks and produce comparable results."""


@cli.command("list-benchmarks")
def cmd_list_benchmarks() -> None:
    """List the benchmarks bundled with this harness."""
    table = Table(title="Available benchmarks")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    for name, desc in list_benchmarks():
        table.add_row(name, desc)
    console.print(table)


@cli.command("list-systems")
def cmd_list_systems() -> None:
    """List the memory systems supported by adapters."""
    table = Table(title="Available systems (adapters)")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="white")
    for name, desc in list_adapters():
        table.add_row(name, desc)
    console.print(table)


@cli.command("run")
@click.option(
    "--benchmark",
    "benchmark_name",
    required=True,
    type=click.Choice([b for b, _ in list_benchmarks()]),
    help="Benchmark to run.",
)
@click.option(
    "--systems",
    default="all",
    help="Comma-separated list of systems, or 'all'.",
)
@click.option(
    "--output",
    "output_dir",
    default="results",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Directory where results will be written.",
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit the number of episodes (useful for smoke tests).",
)
@click.option(
    "--mock",
    is_flag=True,
    default=False,
    help="Run with the mock adapter only (no API keys required).",
)
def cmd_run(
    benchmark_name: str,
    systems: str,
    output_dir: Path,
    limit: int | None,
    mock: bool,
) -> None:
    """Execute a benchmark across one or more systems."""
    seed_env = os.environ.get("LEDGERMEM_EVAL_SEED")
    # `str.isdigit()` rejects negative seeds and any leading whitespace, so
    # it silently falls back to the default. Use a try/except so we honor any
    # signed integer the operator passes.
    if seed_env:
        try:
            seed = int(seed_env)
        except ValueError:
            seed = DEFAULT_EVAL_SEED
    else:
        seed = DEFAULT_EVAL_SEED
    random.seed(seed)
    try:
        import numpy as np  # type: ignore[import-not-found]

        np.random.seed(seed)
    except ImportError:
        pass
    # pandas 2.x no longer routes `DataFrame.sample()` through `np.random` by
    # default — it uses a fresh `np.random.default_rng()` per call unless an
    # explicit `random_state` is supplied. Surface the seed via an env var so
    # adapters that use pandas can pick it up and stay reproducible.
    os.environ.setdefault("LEDGERMEM_EVAL_RANDOM_STATE", str(seed))

    if mock:
        chosen_systems = ["mock"]
    elif systems == "all":
        chosen_systems = [name for name, _ in list_adapters() if name != "mock"]
    else:
        chosen_systems = [s.strip() for s in systems.split(",") if s.strip()]

    benchmark = build_benchmark(benchmark_name, limit=limit)
    output_dir.mkdir(parents=True, exist_ok=True)

    overall_table = Table(title=f"{benchmark_name} — summary")
    overall_table.add_column("System", style="cyan")
    overall_table.add_column("Recall@5", justify="right")
    overall_table.add_column("Precision@5", justify="right")
    overall_table.add_column("F1", justify="right")
    overall_table.add_column("p50 (ms)", justify="right")
    overall_table.add_column("p95 (ms)", justify="right")

    for system_name in chosen_systems:
        console.rule(f"[bold cyan]{system_name}[/bold cyan]")
        adapter = build_adapter(system_name)
        run_record = benchmark.run(adapter)
        metrics = score_run(run_record)
        path = write_results(
            output_dir=output_dir,
            benchmark=benchmark_name,
            system=system_name,
            metrics=metrics,
            run=run_record,
        )
        console.print(f"[green]wrote[/green] {path}")
        overall_table.add_row(
            system_name,
            f"{metrics.recall_at_k:.3f}",
            f"{metrics.precision_at_k:.3f}",
            f"{metrics.f1:.3f}",
            f"{metrics.latency_p50_ms:.0f}",
            f"{metrics.latency_p95_ms:.0f}",
        )

    console.print(overall_table)


def main() -> int:
    try:
        cli(standalone_mode=False)
    except click.exceptions.Abort:
        return 130
    except click.ClickException as exc:
        exc.show()
        return exc.exit_code
    return 0


if __name__ == "__main__":
    sys.exit(main())
