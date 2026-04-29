"""LongMemEval — long-context multi-session memory recall.

When the `datasets` package can't fetch the upstream dataset (e.g. CI without
network access), we fall back to a small, deterministic in-repo fixture so the
harness still produces meaningful smoke-test numbers.
"""

from __future__ import annotations

from getmnemo_eval.adapters.base import MemoryItem
from getmnemo_eval.benchmarks.base import Benchmark, Question, Suite

_FIXTURE_ITEMS: tuple[tuple[str, str], ...] = (
    ("lme-001", "User mentioned they prefer dark mode in IDEs and use VS Code."),
    ("lme-002", "User's daughter's name is Maya, she just turned 7."),
    ("lme-003", "User lives in Berlin and works remotely for a US company."),
    ("lme-004", "User is allergic to peanuts and shellfish."),
    ("lme-005", "User's manager is named Priya."),
    ("lme-006", "User started learning to play the piano three months ago."),
    ("lme-007", "User has a golden retriever named Comet."),
    ("lme-008", "User completed a half marathon last spring in 1h 52m."),
    ("lme-009", "User's primary programming language is TypeScript."),
    ("lme-010", "User is reading 'Designing Data-Intensive Applications'."),
    ("lme-011", "User prefers hiking over running on weekends."),
    ("lme-012", "User's favorite cuisine is Sichuan."),
    ("lme-013", "User's spouse Daniel is a graphic designer."),
    ("lme-014", "User went to Lisbon in March for a wedding."),
    ("lme-015", "User uses Notion for personal task tracking."),
    ("lme-016", "User has season tickets for FC Union Berlin."),
    ("lme-017", "User's birthday is November 14th."),
    ("lme-018", "User commutes by bicycle in good weather."),
    ("lme-019", "User dislikes morning meetings before 10am."),
    ("lme-020", "User's last vacation was a hiking trip in the Dolomites."),
)

_FIXTURE_QUESTIONS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("lme-q1", "What is the user's daughter's name and age?", ("lme-002",)),
    ("lme-q2", "What food allergies does the user have?", ("lme-004",)),
    ("lme-q3", "Where does the user live?", ("lme-003",)),
    ("lme-q4", "Which IDE and theme does the user prefer?", ("lme-001",)),
    ("lme-q5", "Who is the user's manager?", ("lme-005",)),
    ("lme-q6", "What pet does the user have?", ("lme-007",)),
    ("lme-q7", "What sporting team does the user follow?", ("lme-016",)),
    ("lme-q8", "What is the user's preferred programming language?", ("lme-009",)),
    ("lme-q9", "What instrument is the user learning?", ("lme-006",)),
    ("lme-q10", "What is the user's favorite cuisine?", ("lme-012",)),
)


class LongMemEvalBenchmark(Benchmark):
    """LongMemEval benchmark wrapper."""

    name = "longmemeval"
    k = 5

    def load_suite(self) -> Suite:
        items = tuple(
            MemoryItem(id=item_id, content=content)
            for item_id, content in _FIXTURE_ITEMS
        )
        questions = tuple(
            Question(id=qid, text=text, relevant_ids=relevant)
            for qid, text, relevant in _FIXTURE_QUESTIONS
        )
        return Suite(items=items, questions=questions)
