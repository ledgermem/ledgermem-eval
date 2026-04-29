"""Mnemo adapter — talks to api.getmnemo.xyz via the public REST API."""

from __future__ import annotations

import os
from typing import Any

import httpx

from getmnemo_eval.adapters.base import Adapter, MemoryItem, SearchResult


class MnemoAdapter(Adapter):
    """Adapter for Mnemo managed memory."""

    name = "getmnemo"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        workspace_id: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._base_url = (base_url or os.environ.get("GETMNEMO_BASE_URL", "https://api.getmnemo.xyz")).rstrip("/")
        self._api_key = api_key or os.environ.get("GETMNEMO_API_KEY", "")
        self._workspace_id = workspace_id or os.environ.get("GETMNEMO_WORKSPACE_ID", "")
        self._timeout = timeout
        self._client: httpx.Client | None = None

    def setup(self) -> None:
        if not self._api_key or not self._workspace_id:
            raise RuntimeError(
                "GETMNEMO_API_KEY and GETMNEMO_WORKSPACE_ID must be set "
                "to use the Mnemo adapter."
            )
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "x-workspace-id": self._workspace_id,
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
            "id": item.id,
            "content": item.content,
            "metadata": item.metadata or {},
        }
        response = self._http().post("/v1/memories", json=body)
        response.raise_for_status()

    def search(self, query: str, k: int) -> list[SearchResult]:
        response = self._http().post(
            "/v1/search",
            json={"query": query, "limit": k},
        )
        response.raise_for_status()
        payload = response.json()
        hits = payload.get("results") or payload.get("data") or []
        return [
            SearchResult(
                id=str(hit.get("id")),
                content=str(hit.get("content", "")),
                score=float(hit.get("score", 0.0)),
                metadata=hit.get("metadata"),
            )
            for hit in hits
        ]
