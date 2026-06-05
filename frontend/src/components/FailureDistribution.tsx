import type { FailureRow } from "@/lib/metrics";

export function FailureDistribution({ rows }: { rows: FailureRow[] }) {
  const max = Math.max(...rows.map((row) => row.count), 1);

  return (
    <div className="panel p-5">
      <div className="mb-5 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-graphite">Failure distribution</h2>
        <span className="text-xs text-slate-500">{rows.reduce((sum, row) => sum + row.count, 0)} failures</span>
      </div>
      <div className="space-y-3">
        {rows.length ? rows.map((row) => (
          <div key={row.reason}>
            <div className="mb-1 flex items-center justify-between text-sm">
              <span className="font-medium text-slate-700">{row.reason}</span>
              <span className="text-slate-500">{row.count}</span>
            </div>
            <div className="h-2 rounded bg-slate-100">
              <div className="h-2 rounded bg-danger" style={{ width: `${(row.count / max) * 100}%` }} />
            </div>
          </div>
        )) : (
          <div className="rounded-md border border-dashed border-line bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
            No failures recorded.
          </div>
        )}
      </div>
    </div>
  );
}
