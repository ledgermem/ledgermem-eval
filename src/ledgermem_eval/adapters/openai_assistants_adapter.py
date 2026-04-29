"""OpenAI Assistants adapter — uses thread state as the memory store."""

from __future__ import annotations

import os
from typing import Any

import httpx

from getmnemo_eval.adapters.base import Adapter, MemoryItem, SearchResult


class OpenAIAssistantsAdapter(Adapter):
    """Adapter using OpenAI Assistants threads as memory."""

    name = "openai-assistants"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        thread_id: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        timeout: float = 30.0,
    ) -> None:
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self._thread_id = thread_id
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: httpx.Client | None = None

    def setup(self) -> None:
        if not self._api_key:
            raise RuntimeError("OPENAI_API_KEY must be set to use the OpenAI Assistants adapter.")
        self._client = httpx.Client(
            base_url=self._base_url,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
                "OpenAI-Beta": "assistants=v2",
            },
            timeout=self._timeout,
        )
        if self._thread_id is None:
            response = self._client.post("/threads", json={})
            response.raise_for_status()
            self._thread_id = response.json()["id"]

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
            "role": "user",
            "content": item.content,
            "metadata": {"external_id": item.id, **(item.metadata or {})},
        }
        response = self._http().post(
            f"/threads/{self._thread_id}/messages",
            json=body,
        )
        response.raise_for_status()

    def search(self, query: str, k: int) -> list[SearchResult]:
        response = self._http().get(
            f"/threads/{self._thread_id}/messages",
            params={"limit": min(100, max(k * 4, 20)), "order": "desc"},
        )
        response.raise_for_status()
        messages = response.json().get("data", [])
        from getmnemo_eval.adapters.baseline_adapter import _cosine, _tokens

        query_tokens = _tokens(query)
        scored: list[tuple[float, dict[str, Any]]] = []
        for msg in messages:
            content_blocks = msg.get("content", [])
            text = " ".join(
                block.get("text", {}).get("value", "")
                for block in content_blocks
                if block.get("type") == "text"
            )
            score = _cosine(query_tokens, _tokens(text))
            if score > 0:
                scored.append((score, {**msg, "_text": text}))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            SearchResult(
                id=str(msg.get("metadata", {}).get("external_id") or msg.get("id")),
                content=msg["_text"],
                score=score,
                metadata=msg.get("metadata"),
            )
            for score, msg in scored[:k]
        ]
