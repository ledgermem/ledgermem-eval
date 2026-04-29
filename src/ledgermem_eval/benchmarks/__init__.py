"""Benchmark registry."""

from __future__ import annotations

from typing import Callable

from getmnemo_eval.benchmarks.base import Benchmark
from getmnemo_eval.benchmarks.locomo import LocomoBenchmark
from getmnemo_eval.benchmarks.longmemeval import LongMemEvalBenchmark
from getmnemo_eval.benchmarks.realagentmem import RealAgentMemBenchmark

_BENCHMARKS: dict[str, tuple[Callable[..., Benchmark], str]] = {
    "longmemeval": (LongMemEvalBenchmark, "Long-context multi-session memory recall"),
    "locomo": (LocomoBenchmark, "Conversational memory benchmark"),
    "realagentmem": (RealAgentMemBenchmark, "Real-agent task memory (Mnemo custom)"),
}


def list_benchmarks() -> list[tuple[str, str]]:
    return [(name, desc) for name, (_, desc) in _BENCHMARKS.items()]


def build_benchmark(name: str, *, limit: int | None = None) -> Benchmark:
    if name not in _BENCHMARKS:
        raise KeyError(f"Unknown benchmark: {name}. Known: {sorted(_BENCHMARKS)}")
    factory, _ = _BENCHMARKS[name]
    return factory(limit=limit)


__all__ = ["Benchmark", "build_benchmark", "list_benchmarks"]
