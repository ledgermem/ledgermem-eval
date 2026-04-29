"""Result serialization helpers."""

from __future__ import annotations

import json
import os
import platform
import time
import uuid
from dataclasses import asdict
from pathlib import Path

from getmnemo_eval.scoring import RunMetrics, RunRecord


def write_results(
    *,
    output_dir: Path,
    benchmark: str,
    system: str,
    metrics: RunMetrics,
    run: RunRecord,
) -> Path:
    """Persist the run results to `<output_dir>/<benchmark>/<system>/<run-id>.json`."""
    run_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    target_dir = output_dir / benchmark / system
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{run_id}.json"

    payload = {
        "run_id": run_id,
        "benchmark": benchmark,
        "system": system,
        "k": run.k,
        "metrics": metrics.as_dict(),
        "metadata": {
            **run.metadata,
            "host": platform.node(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "harness_version": _harness_version(),
            "git_sha": os.environ.get("GIT_SHA", "unknown"),
        },
        "episodes": [
            {
                "episode_id": ep.episode_id,
                "relevant_ids": list(ep.relevant_ids),
                "retrieved_ids": list(ep.retrieved_ids),
                "latency_ms": ep.latency_ms,
            }
            for ep in run.episodes
        ],
    }
    target_path.write_text(json.dumps(payload, indent=2, default=_default))
    return target_path


def _default(obj: object) -> object:
    if hasattr(obj, "__dataclass_fields__"):
        return asdict(obj)  # type: ignore[arg-type]
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _harness_version() -> str:
    try:
        from importlib.metadata import version

        return version("getmnemo-eval")
    except Exception:
        return "0.1.0"
