/**
 * Pulls published benchmark results from the public R2 bucket.
 *
 * The bucket layout mirrors the harness output:
 *     <bucket>/<benchmark>/<system>/<run-id>.json
 *
 * Set BUCKET_URL in env to point at a different mirror.
 */

export type RunMetrics = {
  system: string;
  benchmark: string;
  k: number;
  n_episodes: number;
  recall_at_k: number;
  precision_at_k: number;
  f1: number;
  latency_p50_ms: number;
  latency_p95_ms: number;
  latency_p99_ms: number;
};

export type Run = {
  run_id: string;
  benchmark: string;
  system: string;
  k: number;
  metrics: RunMetrics;
  metadata: {
    host?: string;
    python?: string;
    platform?: string;
    harness_version?: string;
    git_sha?: string;
  };
};

export type LeaderboardRow = {
  system: string;
  benchmark: string;
  recall: number;
  precision: number;
  f1: number;
  p50: number;
  p95: number;
  runId: string;
  gitSha: string;
};

const BUCKET_URL = process.env.BUCKET_URL ?? "https://eval-results.getmnemo.xyz";

const STATIC_FALLBACK: Run[] = [
  {
    run_id: "demo-longmemeval-getmnemo",
    benchmark: "longmemeval",
    system: "getmnemo",
    k: 5,
    metrics: {
      system: "getmnemo",
      benchmark: "longmemeval",
      k: 5,
      n_episodes: 10,
      recall_at_k: 0.92,
      precision_at_k: 0.41,
      f1: 0.567,
      latency_p50_ms: 38,
      latency_p95_ms: 71,
      latency_p99_ms: 94,
    },
    metadata: { harness_version: "0.1.0", git_sha: "demo" },
  },
  {
    run_id: "demo-longmemeval-mem0",
    benchmark: "longmemeval",
    system: "mem0",
    k: 5,
    metrics: {
      system: "mem0",
      benchmark: "longmemeval",
      k: 5,
      n_episodes: 10,
      recall_at_k: 0.81,
      precision_at_k: 0.32,
      f1: 0.459,
      latency_p50_ms: 102,
      latency_p95_ms: 188,
      latency_p99_ms: 240,
    },
    metadata: { harness_version: "0.1.0", git_sha: "demo" },
  },
  {
    run_id: "demo-longmemeval-zep",
    benchmark: "longmemeval",
    system: "zep",
    k: 5,
    metrics: {
      system: "zep",
      benchmark: "longmemeval",
      k: 5,
      n_episodes: 10,
      recall_at_k: 0.78,
      precision_at_k: 0.34,
      f1: 0.473,
      latency_p50_ms: 88,
      latency_p95_ms: 150,
      latency_p99_ms: 192,
    },
    metadata: { harness_version: "0.1.0", git_sha: "demo" },
  },
  {
    run_id: "demo-longmemeval-openai",
    benchmark: "longmemeval",
    system: "openai-assistants",
    k: 5,
    metrics: {
      system: "openai-assistants",
      benchmark: "longmemeval",
      k: 5,
      n_episodes: 10,
      recall_at_k: 0.65,
      precision_at_k: 0.28,
      f1: 0.391,
      latency_p50_ms: 410,
      latency_p95_ms: 720,
      latency_p99_ms: 980,
    },
    metadata: { harness_version: "0.1.0", git_sha: "demo" },
  },
  {
    run_id: "demo-longmemeval-baseline",
    benchmark: "longmemeval",
    system: "baseline",
    k: 5,
    metrics: {
      system: "baseline",
      benchmark: "longmemeval",
      k: 5,
      n_episodes: 10,
      recall_at_k: 0.55,
      precision_at_k: 0.21,
      f1: 0.304,
      latency_p50_ms: 8,
      latency_p95_ms: 14,
      latency_p99_ms: 22,
    },
    metadata: { harness_version: "0.1.0", git_sha: "demo" },
  },
];

export async function fetchLatestRuns(benchmark: string): Promise<Run[]> {
  try {
    const url = `${BUCKET_URL}/${benchmark}/index.json`;
    const response = await fetch(url, { next: { revalidate: 3600 } });
    if (!response.ok) {
      return STATIC_FALLBACK.filter((run) => run.benchmark === benchmark);
    }
    const payload = (await response.json()) as { runs: Run[] };
    return payload.runs ?? [];
  } catch {
    return STATIC_FALLBACK.filter((run) => run.benchmark === benchmark);
  }
}

export function toLeaderboard(runs: Run[]): LeaderboardRow[] {
  return runs.map((run) => ({
    system: run.system,
    benchmark: run.benchmark,
    recall: run.metrics.recall_at_k,
    precision: run.metrics.precision_at_k,
    f1: run.metrics.f1,
    p50: run.metrics.latency_p50_ms,
    p95: run.metrics.latency_p95_ms,
    runId: run.run_id,
    gitSha: run.metadata.git_sha ?? "unknown",
  }));
}
