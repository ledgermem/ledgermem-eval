"""RealAgentMem — LedgerMem's custom benchmark for real-agent task memory.

The suite focuses on cross-session task continuity: an agent works on a project
over many sessions and must consistently recall earlier decisions, data, and
user preferences. This is the closest published proxy for real production
agent traffic.
"""

from __future__ import annotations

from ledgermem_eval.adapters.base import MemoryItem
from ledgermem_eval.benchmarks.base import Benchmark, Question, Suite

_TASKS: tuple[tuple[str, str], ...] = (
    ("ram-001", "Project Helios: target ship date is 2026-09-15."),
    ("ram-002", "Helios stack decision: PostgreSQL 16 with pgvector for embeddings."),
    ("ram-003", "Helios auth: Clerk for user identity, custom roles in DB."),
    ("ram-004", "Helios billing partner: Stripe; tax engine via Stripe Tax."),
    ("ram-005", "Helios infra target: Cloudflare Workers + R2 for assets."),
    ("ram-006", "Helios CI: GitHub Actions; staging deploy on every PR merge."),
    ("ram-007", "Helios design system: shadcn/ui on top of Tailwind v4."),
    ("ram-008", "Helios analytics: PostHog self-hosted on Hetzner."),
    ("ram-009", "Helios on-call rotation: weekly, 4 engineers, paged via OpsGenie."),
    ("ram-010", "Helios SLO: 99.9% availability for the public API."),
    ("ram-011", "Helios privacy: data residency in EU only; no US replication."),
    ("ram-012", "Helios feature flags: Statsig; flags must be cleaned within 30 days."),
    ("ram-013", "Helios incident retros: blameless, written within 48 hours."),
    ("ram-014", "Helios code review SLA: first response within 4 working hours."),
    ("ram-015", "Helios docs: Fumadocs site at docs.helios.example."),
    ("ram-016", "Helios team standup: Tuesdays and Thursdays at 09:30 CET."),
    ("ram-017", "Helios secrets: stored in Doppler, never in env files."),
    ("ram-018", "Helios test policy: 80% branch coverage minimum, blocked PRs below."),
    ("ram-019", "Helios database migrations: gated behind a manual approval step."),
    ("ram-020", "Helios brand color: #4F46E5 (indigo-600)."),
)

_QUESTIONS: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("ram-q1", "What is the Helios target ship date?", ("ram-001",)),
    ("ram-q2", "Which database does Helios use and which extension for vectors?", ("ram-002",)),
    ("ram-q3", "Which auth provider was selected for Helios?", ("ram-003",)),
    ("ram-q4", "Which billing and tax tools does Helios use?", ("ram-004",)),
    ("ram-q5", "Where is Helios infrastructure hosted?", ("ram-005",)),
    ("ram-q6", "What is the Helios on-call rotation cadence?", ("ram-009",)),
    ("ram-q7", "What is the Helios SLO?", ("ram-010",)),
    ("ram-q8", "What are the Helios data residency rules?", ("ram-011",)),
    ("ram-q9", "What is the Helios feature flag cleanup window?", ("ram-012",)),
    ("ram-q10", "What is the Helios PR review SLA?", ("ram-014",)),
    ("ram-q11", "Where are Helios secrets stored?", ("ram-017",)),
    ("ram-q12", "What is the Helios test coverage minimum?", ("ram-018",)),
    ("ram-q13", "What is the Helios brand color?", ("ram-020",)),
    ("ram-q14", "When are Helios standups?", ("ram-016",)),
    ("ram-q15", "Which design system does Helios use?", ("ram-007",)),
)


class RealAgentMemBenchmark(Benchmark):
    """RealAgentMem benchmark — cross-session project memory."""

    name = "realagentmem"
    k = 5

    def load_suite(self) -> Suite:
        items = tuple(MemoryItem(id=tid, content=text) for tid, text in _TASKS)
        questions = tuple(
            Question(id=qid, text=text, relevant_ids=relevant)
            for qid, text, relevant in _QUESTIONS
        )
        return Suite(items=items, questions=questions)
