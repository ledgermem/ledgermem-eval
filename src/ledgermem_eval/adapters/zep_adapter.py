"""Zep adapter — uses the Zep cloud API."""

from __future__ import annotations

import os
import uuid

import httpx

from getmnemo_eval.adapters.base import Adapter, MemoryItem, SearchResult


class ZepAdapter(Adapter):
    """Adapter for Zep (https://www.getzep.com)."""

    name = "zep"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.getzep.com",
        session_id: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("ZEP_API_KEY", "")
        self._base_url = base_url.rstrip("/")
        self._session_id = session_id or f"getmnemo-eval-{uuid.uuid4().hex[:8]}"
        self._timeout = timeout
        self._client: httpx.Client | None = None
        self._created_session = False

    def setup(self) -> None:
        if not self._api_key:
            raise RuntimeError("ZEP_API_KEY must be set to use the Zep adapter.")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Api-Key {self._api_key}",
                "Content-Type": "application/json",
            },
            timeout=self._timeout,
        )
        self._ensure_session()

    def teardown(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None

    def _http(self) -> httpx.Client:
        if self._client is None:
            self.setup()
        assert self._client is not None
        return self._client

    def _ensure_session(self) -> None:
        if self._created_session:
            return
        try:
            self._http().post(
                "/api/v2/sessions",
                json={"session_id": self._session_id, "user_id": "eval-user"},
            ).raise_for_status()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code != 409:
                raise
        self._created_session = True

    def load_episodes(self, items: list[MemoryItem]) -> None:
        for item in items:
            self.add(item)

    def add(self, item: MemoryItem) -> None:
        response = self._http().post(
            f"/api/v2/sessions/{self._session_id}/memory",
            json={
                "messages": [
                    {"role": "user", "content": item.content, "metadata": item.metadata or {}}
                ]
            },
        )
        response.raise_for_status()

    def search(self, query: str, k: int) -> list[SearchResult]:
        response = self._http().post(
            f"/api/v2/sessions/{self._session_id}/memory/search",
            json={"text": query, "limit": k},
        )
        response.raise_for_status()
        payload = response.json()
        hits = payload.get("results") or payload.get("messages") or []
        return [
            SearchResult(
                id=str(hit.get("uuid") or hit.get("id")),
                content=str(hit.get("content") or hit.get("message", {}).get("content", "")),
                score=float(hit.get("score") or hit.get("dist", 0.0)),
                metadata=hit.get("metadata"),
            )
            for hit in hits[:k]
        ]
