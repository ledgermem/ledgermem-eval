"""Benchmark base class.

A benchmark is a small, reproducible suite. It owns:
    - the list of episodes (memory items + queries)
    - the run loop (load -> evaluate -> record)
"""

from __future__ import annotations

import abc
import time
from dataclasses import dataclass

from ledgermem_eval.adapters.base import Adapter, MemoryItem
from ledgermem_eval.scoring import EpisodeResult, RunRecord


@dataclass(frozen=True)
class Question:
    """A single benchmark question."""

    id: str
    text: str
    relevant_ids: tuple[str, ...]


@dataclass(frozen=True)
class Suite:
    """A benchmark suite: items to load, then questions to answer."""

    items: tuple[MemoryItem, ...]
    questions: tuple[Question, ...]


class Benchmark(abc.ABC):
    """Abstract benchmark."""

    name: str = "abstract"
    k: int = 5

    def __init__(self, *, limit: int | None = None) -> None:
        self.limit = limit

    @abc.abstractmethod
    def load_suite(self) -> Suite:
        """Return the items + questions for this benchmark."""

    def run(self, adapter: Adapter) -> RunRecord:
        """Drive the adapter through the suite and capture results."""
        adapter.setup()
        try:
            suite = self.load_suite()
            adapter.load_episodes(list(suite.items))
            questions = suite.questions
            if self.limit is not None:
                questions = questions[: self.limit]
            episode_results: list[EpisodeResult] = []
            for question in questions:
                start = time.perf_counter()
                hits = adapter.evaluate(question.text, k=self.k)
                latency_ms = (time.perf_counter() - start) * 1000.0
                episode_results.append(
                    EpisodeResult(
                        episode_id=question.id,
                        relevant_ids=question.relevant_ids,
                        retrieved_ids=tuple(hit.id for hit in hits),
                        latency_ms=latency_ms,
                    )
                )
            return RunRecord(
                system=adapter.name,
                benchmark=self.name,
                k=self.k,
                episodes=tuple(episode_results),
                metadata={"item_count": len(suite.items), "question_count": len(questions)},
            )
        finally:
            adapter.teardown()
