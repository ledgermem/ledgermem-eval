"""Adapter registry — maps a system name to a concrete `Adapter` implementation."""

from __future__ import annotations

from typing import Callable

from ledgermem_eval.adapters.base import Adapter
from ledgermem_eval.adapters.baseline_adapter import BaselineAdapter
from ledgermem_eval.adapters.ledgermem_adapter import LedgerMemAdapter
from ledgermem_eval.adapters.mem0_adapter import Mem0Adapter
from ledgermem_eval.adapters.openai_assistants_adapter import OpenAIAssistantsAdapter
from ledgermem_eval.adapters.zep_adapter import ZepAdapter

_ADAPTERS: dict[str, tuple[Callable[[], Adapter], str]] = {
    "ledgermem": (LedgerMemAdapter, "LedgerMem managed memory (api.proofly.dev)"),
    "mem0": (Mem0Adapter, "Mem0 OSS memory layer"),
    "zep": (ZepAdapter, "Zep memory store"),
    "openai-assistants": (OpenAIAssistantsAdapter, "OpenAI Assistants thread memory"),
    "baseline": (BaselineAdapter, "Stuff-everything-in-context baseline"),
    "mock": (BaselineAdapter, "Mock adapter — uses baseline, no network calls"),
}


def list_adapters() -> list[tuple[str, str]]:
    return [(name, desc) for name, (_, desc) in _ADAPTERS.items()]


def build_adapter(name: str) -> Adapter:
    if name not in _ADAPTERS:
        raise KeyError(f"Unknown adapter: {name}. Known: {sorted(_ADAPTERS)}")
    factory, _ = _ADAPTERS[name]
    return factory()


__all__ = ["Adapter", "build_adapter", "list_adapters"]
