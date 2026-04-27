"""Mem0 adapter — uses the Mem0 cloud API."""

from __future__ import annotations

import os
from typing import Any

import httpx

from ledgermem_eval.adapters.base import Adapter, MemoryItem, SearchResult


class Mem0Adapter(Adapter):
    """Adapter for Mem0 (https://mem0.ai)."""

    name = "mem0"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        user_id: str | None = None,
        base_url: str = "https://api.mem0.ai",
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("MEM0_API_KEY", "")
        self._user_id = user_id or os.environ.get("MEM0_USER_ID", "ledgermem-eval")
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.Client | None = None

    def setup(self) -> None:
        if not self._api_key:
            raise RuntimeError("MEM0_API_KEY must be set to use the Mem0 adapter.")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Token {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=self._timeout,
        )

    def teardown(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def _http(self) -> httpx.Client:
        if self._client is None:
            self.setup()
        assert self._client is not None
        return self._client

    def load_episodes(self, items: list[MemoryItem]) -> None:
        for item in items:
            self.add(item)

    def add(self, item: MemoryItem) -> None:
        body: dict[str, Any] = {
            "messages": [{"role": "user", "content": item.content}],
            "user_id": self._user_id,
            "metadata": {**(item.metadata or {}), "external_id": item.id},
        }
        response = self._http().post("/v1/memories/", json=body)
        response.raise_for_status()

    def search(self, query: str, k: int) -> list[SearchResult]:
        response = self._http().post(
            "/v1/memories/search/",
            json={"query": query, "user_id": self._user_id, "limit": k},
        )
        response.raise_for_status()
        payload = response.json()
        hits = payload if isinstance(payload, list) else payload.get("memories", [])
        results: list[SearchResult] = []
        for hit in hits[:k]:
            metadata = hit.get("metadata") or {}
            results.append(
                SearchResult(
                    id=str(metadata.get("external_id") or hit.get("id")),
                    content=str(hit.get("memory") or hit.get("text") or ""),
                    score=float(hit.get("score", 0.0)),
                    metadata=metadata,
                )
            )
        return results
