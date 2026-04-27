"""Adapter base class.

An Adapter wraps a memory system so the harness can drive it uniformly:
    - load_episodes: receive a series of (user, assistant) turns to persist
    - add: write a single fact/episode to memory
    - search: read top-k matching items for a query
    - evaluate: return the system's answer to a benchmark question
"""

from __future__ import annotations

import abc
from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryItem:
    """A single piece of memory to be stored or retrieved."""

    id: str
    content: str
    metadata: dict | None = None


@dataclass(frozen=True)
class SearchResult:
    """A single search hit returned by an adapter."""

    id: str
    content: str
    score: float
    metadata: dict | None = None


class Adapter(abc.ABC):
    """Abstract base for memory-system adapters."""

    name: str = "abstract"

    def setup(self) -> None:
        """Optional: prepare resources before the run starts."""

    def teardown(self) -> None:
        """Optional: release resources after the run completes."""

    @abc.abstractmethod
    def load_episodes(self, items: list[MemoryItem]) -> None:
        """Bulk-load memory items into the system."""

    @abc.abstractmethod
    def add(self, item: MemoryItem) -> None:
        """Persist a single memory item."""

    @abc.abstractmethod
    def search(self, query: str, k: int) -> list[SearchResult]:
        """Return up to k items relevant to `query`, ordered best-first."""

    def evaluate(self, query: str, k: int) -> list[SearchResult]:
        """Default evaluator — wraps `search`. Subclasses can override for RAG."""
        return self.search(query, k)
