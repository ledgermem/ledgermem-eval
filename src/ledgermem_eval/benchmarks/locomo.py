"""LoCoMo — conversational memory benchmark.

We ship a synthetic 5-conversation fixture that exercises cross-session recall.
"""

from __future__ import annotations

from ledgermem_eval.adapters.base import MemoryItem
from ledgermem_eval.benchmarks.base import Benchmark, Question, Suite

_TURNS: tuple[tuple[str, str, str], ...] = (
    # (id, conversation_id, content)
    ("lc-01-01", "c1", "Alex: I'm planning a trip to Tokyo next April for the cherry blossoms."),
    ("lc-01-02", "c1", "Bot: Nice! For how long?"),
    ("lc-01-03", "c1", "Alex: Two weeks. I want to do at least one ryokan stay."),
    ("lc-02-01", "c2", "Alex: My new job starts on May 1st as a backend engineer at Stripe."),
    ("lc-02-02", "c2", "Bot: Congrats! Will you be relocating?"),
    ("lc-02-03", "c2", "Alex: Yes, moving from Austin to Dublin."),
    ("lc-03-01", "c3", "Alex: I broke my left wrist skateboarding last weekend."),
    ("lc-03-02", "c3", "Bot: Ouch — surgery needed?"),
    ("lc-03-03", "c3", "Alex: No, just a cast for six weeks."),
    ("lc-04-01", "c4", "Alex: I'm reading 'The Three-Body Problem' and loving it."),
    ("lc-04-02", "c4", "Bot: Is this your first Liu Cixin novel?"),
    ("lc-04-03", "c4", "Alex: Yes, but I plan to read the whole trilogy."),
    ("lc-05-01", "c5", "Alex: I adopted a cat named Luna last week."),
    ("lc-05-02", "c5", "Bot: How old?"),
    ("lc-05-03", "c5", "Alex: She's two years old, a tortoiseshell."),
)

_QUESTIONS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("lc-q1", "When is Alex starting his new job and where?", ("lc-02-01", "lc-02-03")),
    ("lc-q2", "What injury did Alex sustain recently?", ("lc-03-01", "lc-03-03")),
    ("lc-q3", "Where is Alex relocating to?", ("lc-02-03",)),
    ("lc-q4", "What is the name and breed of Alex's new pet?", ("lc-05-01", "lc-05-03")),
    ("lc-q5", "Which book is Alex currently reading?", ("lc-04-01",)),
    ("lc-q6", "What month is Alex visiting Tokyo and why?", ("lc-01-01",)),
    ("lc-q7", "How long is Alex's Tokyo trip?", ("lc-01-03",)),
    ("lc-q8", "What city is Alex moving from?", ("lc-02-03",)),
)


class LocomoBenchmark(Benchmark):
    """LoCoMo benchmark wrapper."""

    name = "locomo"
    k = 5

    def load_suite(self) -> Suite:
        items = tuple(
            MemoryItem(id=turn_id, content=content, metadata={"conversation": conv_id})
            for turn_id, conv_id, content in _TURNS
        )
        questions = tuple(
            Question(id=qid, text=text, relevant_ids=relevant)
            for qid, text, relevant in _QUESTIONS
        )
        return Suite(items=items, questions=questions)
