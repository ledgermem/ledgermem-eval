"""Mnemo evaluation harness.

Public benchmark suite for comparing memory systems across standardized tasks.
"""

from getmnemo_eval.scoring import RunMetrics, score_run

__version__ = "0.1.0"
__all__ = ["RunMetrics", "score_run", "__version__"]
