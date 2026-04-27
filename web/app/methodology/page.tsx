export default function MethodologyPage() {
  return (
    <article className="prose max-w-none">
      <h1>Methodology</h1>

      <p>
        We optimize for one thing: results that survive replication. The harness
        is open source, the seed data is in the repo, and every published number
        carries the git SHA of the harness used to produce it.
      </p>

      <h2>Anti-bias rules</h2>
      <ul>
        <li>
          <strong>No system tunes the harness.</strong> Adapter authors may not
          modify the scoring code, the benchmark fixtures, or the run loop. PRs
          that touch those files require a review from someone who is not a
          maintainer of any benchmarked system.
        </li>
        <li>
          <strong>Same model budget for every system.</strong> When a benchmark
          requires generation, all systems get the same model (claude-haiku-4.5
          by default) and the same maximum context budget.
        </li>
        <li>
          <strong>No private fixtures.</strong> Every question and every
          relevant-id mapping is in this repo. Maintainers do not get a private
          dev set.
        </li>
        <li>
          <strong>Latency includes the network.</strong> We do not strip
          round-trip time. Self-hosted systems and cloud systems are reported
          on the same axis.
        </li>
        <li>
          <strong>Failures count.</strong> A timeout, a 5xx, or a malformed
          response is recorded as <code>recall = 0</code> for that episode.
        </li>
      </ul>

      <h2>Scoring</h2>
      <p>
        For each question we compute recall@k and precision@k against the set
        of relevant memory IDs. The benchmark default is k = 5. F1 is the
        harmonic mean of mean-recall and mean-precision over all questions in
        the run.
      </p>
      <p>
        Latency percentiles are computed across all per-query latencies in the
        run, including any queue or network time.
      </p>

      <h2>Reproducibility</h2>
      <pre>
        <code>{`docker pull ledgermem/eval:latest
docker run --rm \\
  -e LEDGERMEM_API_KEY=... \\
  -e LEDGERMEM_WORKSPACE_ID=... \\
  -e MEM0_API_KEY=... \\
  -e ZEP_API_KEY=... \\
  -e OPENAI_API_KEY=... \\
  -v "$PWD/results:/work/results" \\
  ledgermem/eval run --benchmark longmemeval --systems all --output /work/results`}</code>
      </pre>

      <h2>Submitting a system</h2>
      <ol>
        <li>Open a PR adding an adapter under <code>src/ledgermem_eval/adapters/</code>.</li>
        <li>Provide a free-tier or trial key the cron job can use.</li>
        <li>The quarterly cron will start including your system automatically.</li>
      </ol>
    </article>
  );
}
