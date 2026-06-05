import { PolicyComparisonChart } from "@/components/PolicyComparisonChart";
import { getEpisodes, getExperiments } from "@/lib/api";
import { buildPolicyRows } from "@/lib/metrics";

export default async function ComparisonPage() {
  const [episodes, experiments] = await Promise.all([getEpisodes({ limit: 500 }), getExperiments()]);
  const rows = buildPolicyRows(experiments, episodes);

  return (
    <div className="space-y-5">
      <PolicyComparisonChart rows={rows} expanded />
      <div className="panel overflow-x-auto">
        <table className="w-full min-w-[860px] border-collapse">
          <thead className="table-header">
            <tr>
              <th className="px-4 py-3">Policy</th>
              <th className="px-4 py-3">Episodes</th>
              <th className="px-4 py-3">Success</th>
              <th className="px-4 py-3">Avg duration</th>
              <th className="px-4 py-3">Collisions</th>
              <th className="px-4 py-3">Jerk</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.policy}>
                <td className="table-cell font-medium text-graphite">{row.policy}</td>
                <td className="table-cell">{row.episodes}</td>
                <td className="table-cell">{Math.round(row.successRate * 100)}%</td>
                <td className="table-cell">{row.avgDuration.toFixed(2)}s</td>
                <td className="table-cell">{row.avgCollisions.toFixed(2)}</td>
                <td className="table-cell">{row.avgJerk.toFixed(3)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
