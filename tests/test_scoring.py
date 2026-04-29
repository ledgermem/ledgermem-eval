"""Unit tests for the scoring module."""

from __future__ import annotations

import pytest

from getmnemo_eval.scoring import EpisodeResult, RunRecord, _percentile, score_run


def make_episode(
    *,
    episode_id: str = "ep-1",
    relevant: tuple[str, ...] = ("a", "b"),
    retrieved: tuple[str, ...] = ("a", "b", "c", "d", "e"),
    latency_ms: float = 100.0,
) -> EpisodeResult:
    return EpisodeResult(
        episode_id=episode_id,
        relevant_ids=relevant,
        retrieved_ids=retrieved,
        latency_ms=latency_ms,
    )


def make_run(episodes: tuple[EpisodeResult, ...], k: int = 5) -> RunRecord:
    return RunRecord(system="x", benchmark="y", k=k, episodes=episodes)


class TestPercentile:
    def test_empty(self) -> None:
        assert _percentile([], 50) == 0.0

    def test_single(self) -> None:
        assert _percentile([42.0], 95) == 42.0

    def test_p50_odd(self) -> None:
        assert _percentile([1.0, 2.0, 3.0, 4.0, 5.0], 50) == 3.0

    def test_p95(self) -> None:
        result = _percentile([float(i) for i in range(1, 101)], 95)
        assert 95.0 <= result <= 96.0


class TestScoreRun:
    def test_empty_run(self) -> None:
        run = make_run(())
        metrics = score_run(run)
        assert metrics.n_episodes == 0
        assert metrics.recall_at_k == 0.0
        assert metrics.f1 == 0.0

    def test_perfect_recall(self) -> None:
        run = make_run((make_episode(),))
        metrics = score_run(run)
        assert metrics.recall_at_k == 1.0

    def test_zero_recall(self) -> None:
        run = make_run(
            (
                make_episode(
                    relevant=("x", "y"),
                    retrieved=("a", "b", "c", "d", "e"),
                ),
            )
        )
        metrics = score_run(run)
        assert metrics.recall_at_k == 0.0
        assert metrics.precision_at_k == 0.0

    def test_partial_recall(self) -> None:
        run = make_run(
            (
                make_episode(
                    relevant=("a", "b", "c", "d"),
                    retrieved=("a", "b", "x", "y", "z"),
                ),
            )
        )
        metrics = score_run(run)
        assert metrics.recall_at_k == pytest.approx(0.5)
        assert metrics.precision_at_k == pytest.approx(0.4)
        assert metrics.f1 == pytest.approx(2 * 0.5 * 0.4 / (0.5 + 0.4))

    def test_latency_aggregation(self) -> None:
        run = make_run(
            tuple(
                make_episode(episode_id=f"ep-{i}", latency_ms=float(i * 10))
                for i in range(1, 11)
            )
        )
        metrics = score_run(run)
        assert metrics.latency_p50_ms == pytest.approx(55.0)
        assert metrics.latency_p95_ms == pytest.approx(95.5, abs=0.5)


def test_full_baseline_run_smoke() -> None:
    """End-to-end smoke test using the baseline adapter and longmemeval."""
    from getmnemo_eval.adapters.baseline_adapter import BaselineAdapter
    from getmnemo_eval.benchmarks.longmemeval import LongMemEvalBenchmark

    benchmark = LongMemEvalBenchmark()
    adapter = BaselineAdapter()
    run = benchmark.run(adapter)
    metrics = score_run(run)
    assert metrics.n_episodes > 0
    # baseline should at least beat zero on the synthetic fixture
    assert metrics.recall_at_k > 0.0
