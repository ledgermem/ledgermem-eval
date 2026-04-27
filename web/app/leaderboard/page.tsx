import { ParetoChart } from "@/components/ParetoChart";
import { ResultTable } from "@/components/ResultTable";
import { fetchLatestRuns, toLeaderboard } from "@/lib/results";

const BENCHMARKS = ["longmemeval", "locomo", "realagentmem"] as const;

export default async function LeaderboardPage() {
  const sections = await Promise.all(
    BENCHMARKS.map(async (benchmark) => {
      const runs = await fetchLatestRuns(benchmark);
      return { benchmark, rows: toLeaderboard(runs) };
    }),
  );

  return (
    <div className="space-y-12">
      <header>
        <h1 className="text-3xl font-bold">Leaderboard</h1>
        <p className="mt-2 text-neutral-600">
          Latest published runs by benchmark. Click a system name to see its
          full run history (coming soon — submit a PR).
        </p>
      </header>

      {sections.map(({ benchmark, rows }) => (
        <section key={benchmark} className="space-y-6">
          <h2 className="text-2xl font-semibold capitalize">{benchmark}</h2>
          {rows.length === 0 ? (
            <p className="text-neutral-500">No runs published yet.</p>
          ) : (
            <>
              <ResultTable rows={rows} sortBy="f1" />
              <ParetoChart rows={rows} />
            </>
          )}
        </section>
      ))}
    </div>
  );
}
