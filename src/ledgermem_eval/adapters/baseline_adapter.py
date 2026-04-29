"""Baseline adapter — keeps everything in memory and ranks by token overlap.

This is intentionally simple: it lets the harness produce comparable numbers
without any network calls, and it's the floor every other system should beat.
"""

from __future__ import annotations

import re
from collections import Counter

from getmnemo_eval.adapters.base import Adapter, MemoryItem, SearchResult

_TOKENIZER = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> Counter[str]:
    return Counter(_TOKENIZER.findall(text.lower()))


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    overlap = sum(a[token] * b[token] for token in a if token in b)
    if overlap == 0:
        return 0.0
    norm_a = sum(v * v for v in a.values()) ** 0.5
    norm_b = sum(v * v for v in b.values()) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return overlap / (norm_a * norm_b)


class BaselineAdapter(Adapter):
    """Stuff-everything-in-context baseline."""

    name = "baseline"

    def __init__(self) -> None:
        self._items: list[MemoryItem] = []
        self._cached_tokens: dict[str, Counter[str]] = {}

    def load_episodes(self, items: list[MemoryItem]) -> None:
        for item in items:
            self.add(item)

    def add(self, item: MemoryItem) -> None:
        self._items.append(item)
        self._cached_tokens[item.id] = _tokens(item.content)

    def search(self, query: str, k: int) -> list[SearchResult]:
        if not self._items:
            return []
        query_tokens = _tokens(query)
        scored: list[tuple[float, MemoryItem]] = []
        for item in self._items:
            score = _cosine(query_tokens, self._cached_tokens[item.id])
            if score > 0:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            SearchResult(id=item.id, content=item.content, score=score, metadata=item.metadata)
            for score, item in scored[:k]
        ]
