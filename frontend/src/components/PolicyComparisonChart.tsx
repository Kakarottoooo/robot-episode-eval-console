import type { PolicyRow } from "@/lib/metrics";

export function PolicyComparisonChart({
  rows,
  expanded = false,
}: {
  rows: PolicyRow[];
  expanded?: boolean;
}) {
  const maxEpisodes = Math.max(...rows.map((row) => row.episodes), 1);

  return (
    <div className="panel p-5">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-graphite">Policy comparison</h2>
        <span className="text-xs text-slate-500">{rows.length} policies</span>
      </div>
      <div className={expanded ? "space-y-5" : "space-y-4"}>
        {rows.length ? rows.map((row) => (
          <div key={row.policy} className="grid gap-2 md:grid-cols-[180px_1fr_64px] md:items-center">
            <div>
              <div className="truncate text-sm font-medium text-graphite">{row.policy}</div>
              <div className="text-xs text-slate-500">{row.episodes} episodes</div>
            </div>
            <div className="space-y-1">
              <div className="h-2 rounded bg-slate-100">
                <div className="h-2 rounded bg-teal" style={{ width: `${row.successRate * 100}%` }} />
              </div>
              <div className="h-1 rounded bg-slate-100">
                <div className="h-1 rounded bg-cyan" style={{ width: `${(row.episodes / maxEpisodes) * 100}%` }} />
              </div>
            </div>
            <div className="text-right text-sm font-semibold text-graphite">
              {Math.round(row.successRate * 100)}%
            </div>
          </div>
        )) : (
          <div className="rounded-md border border-dashed border-line bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
            No policy data yet.
          </div>
        )}
      </div>
    </div>
  );
}
