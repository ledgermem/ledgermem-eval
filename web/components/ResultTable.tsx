import type { LeaderboardRow } from "@/lib/results";

type Props = {
  rows: LeaderboardRow[];
  sortBy?: keyof LeaderboardRow;
};

export function ResultTable({ rows, sortBy = "f1" }: Props) {
  const sorted = [...rows].sort((a, b) => {
    const av = a[sortBy];
    const bv = b[sortBy];
    if (typeof av === "number" && typeof bv === "number") {
      return sortBy === "p50" || sortBy === "p95" ? av - bv : bv - av;
    }
    return String(av).localeCompare(String(bv));
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
