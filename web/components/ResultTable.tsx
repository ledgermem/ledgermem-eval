import type { LeaderboardRow } from "@/lib/results";

type Props = {
  rows: LeaderboardRow[];
  sortBy?: keyof LeaderboardRow;
};

export function ResultTable({ rows, sortBy = "f1" }: Props) {
  // Stable sort with a deterministic tie-breaker so the leaderboard order does
  // not jitter between renders or runs when two systems share the same score.
  // Tie-break: ascending system name, then ascending runId.
  const sorted = [...rows].sort((a, b) => {
    const av = a[sortBy];
    const bv = b[sortBy];
    let primary = 0;
    if (typeof av === "number" && typeof bv === "number") {
      primary = sortBy === "p50" || sortBy === "p95" ? av - bv : bv - av;
    } else {
      primary = String(av).localeCompare(String(bv));
    }
    if (primary !== 0) return primary;
    const systemCmp = a.system.localeCompare(b.system);
    if (systemCmp !== 0) return systemCmp;
    return a.runId.localeCompare(b.runId);
  });

  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-200">
      <table className="min-w-full divide-y divide-neutral-200 text-sm">
        <thead className="bg-neutral-50 text-left">
          <tr>
            <th className="px-4 py-3 font-semibold">System</th>
            <th className="px-4 py-3 font-semibold">Recall@5</th>
            <th className="px-4 py-3 font-semibold">Precision@5</th>
            <th className="px-4 py-3 font-semibold">F1</th>
            <th className="px-4 py-3 font-semibold">p50 (ms)</th>
            <th className="px-4 py-3 font-semibold">p95 (ms)</th>
            <th className="px-4 py-3 font-semibold">Run ID</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-neutral-100">
          {sorted.map((row) => (
            <tr key={`${row.system}-${row.runId}`}>
              <td className="px-4 py-3 font-medium">{row.system}</td>
              <td className="px-4 py-3 tabular-nums">{row.recall.toFixed(3)}</td>
              <td className="px-4 py-3 tabular-nums">{row.precision.toFixed(3)}</td>
              <td className="px-4 py-3 tabular-nums">{row.f1.toFixed(3)}</td>
              <td className="px-4 py-3 tabular-nums">{row.p50.toFixed(0)}</td>
              <td className="px-4 py-3 tabular-nums">{row.p95.toFixed(0)}</td>
              <td className="px-4 py-3 font-mono text-xs text-neutral-500">{row.runId}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
