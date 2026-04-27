"""Scoring utilities for benchmark runs.

We score each run on:
    - recall@k: fraction of relevant items present in the top-k retrieved items
    - precision@k: fraction of top-k items that are relevant
    - F1: harmonic mean of recall and precision
    - latency p50/p95/p99 (ms)

A "run" is a list of `EpisodeResult` objects describing what was retrieved for
each evaluation question and how long retrieval took.
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Iterable, Sequence


@dataclass(frozen=True)
class EpisodeResult:
    """Outcome of evaluating a single question against a memory system."""

    episode_id: str
    relevant_ids: tuple[str, ...]
    retrieved_ids: tuple[str, ...]
    latency_ms: float


@dataclass(frozen=True)
class RunRecord:
    """A complete benchmark run for a single (system, benchmark) pair."""

    system: str
    benchmark: str
    k: int
    episodes: tuple[EpisodeResult, ...]
    metadata: dict = field(default_factory=dict)


@dataclass(frozen=True)
class RunMetrics:
    """Aggregated metrics across all episodes in a run."""

    system: str
    benchmark: str
    k: int
    n_episodes: int
    recall_at_k: float
    precision_at_k: float
    f1: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float

    def as_dict(self) -> dict:
        return {
            "system": self.system,
            "benchmark": self.benchmark,
            "k": self.k,
            "n_episodes": self.n_episodes,
            "recall_at_k": self.recall_at_k,
            "precision_at_k": self.precision_at_k,
            "f1": self.f1,
            "latency_p50_ms": self.latency_p50_ms,
            "latency_p95_ms": self.latency_p95_ms,
            "latency_p99_ms": self.latency_p99_ms,
        }


def _percentile(values: Sequence[float], percentile: float) -> float:
    """Return the requested percentile (0 to 100) of `values`."""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    if len(sorted_values) == 1:
        return float(sorted_values[0])
    rank = (percentile / 100.0) * (len(sorted_values) - 1)
    lower_idx = int(rank)
    upper_idx = min(lower_idx + 1, len(sorted_values) - 1)
    weight = rank - lower_idx
    return float(sorted_values[lower_idx] * (1 - weight) + sorted_values[upper_idx] * weight)


def _safe_div(numerator: float, denominator: float) -> float:
    return float(numerator / denominator) if denominator else 0.0


def _episode_recall(relevant: Iterable[str], retrieved: Sequence[str], k: int) -> float:
    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    top_k = set(retrieved[:k])
    return _safe_div(len(top_k & relevant_set), len(relevant_set))


def _episode_precision(relevant: Iterable[str], retrieved: Sequence[str], k: int) -> float:
    if not retrieved:
        return 0.0
    top_k = retrieved[:k]
    if not top_k:
        return 0.0
    relevant_set = set(relevant)
    hits = sum(1 for rid in top_k if rid in relevant_set)
    return _safe_div(hits, len(top_k))


def score_run(run: RunRecord) -> RunMetrics:
    """Aggregate per-episode results into a single `RunMetrics`."""
    episodes = run.episodes
    if not episodes:
        return RunMetrics(
            system=run.system,
            benchmark=run.benchmark,
            k=run.k,
            n_episodes=0,
            recall_at_k=0.0,
            precision_at_k=0.0,
            f1=0.0,
            latency_p50_ms=0.0,
            latency_p95_ms=0.0,
            latency_p99_ms=0.0,
        )

    recalls = [_episode_recall(ep.relevant_ids, ep.retrieved_ids, run.k) for ep in episodes]
    precisions = [_episode_precision(ep.relevant_ids, ep.retrieved_ids, run.k) for ep in episodes]
    latencies = [ep.latency_ms for ep in episodes]

    mean_recall = statistics.mean(recalls)
    mean_precision = statistics.mean(precisions)
    f1 = (
        2 * mean_recall * mean_precision / (mean_recall + mean_precision)
        if (mean_recall + mean_precision) > 0
        else 0.0
    )

    return RunMetrics(
        system=run.system,
        benchmark=run.benchmark,
        k=run.k,
        n_episodes=len(episodes),
        recall_at_k=mean_recall,
        precision_at_k=mean_precision,
        f1=f1,
        latency_p50_ms=_percentile(latencies, 50),
        latency_p95_ms=_percentile(latencies, 95),
        latency_p99_ms=_percentile(latencies, 99),
    )
