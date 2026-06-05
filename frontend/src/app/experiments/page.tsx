import { getExperiments } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export default async function ExperimentsPage() {
  const experiments = await getExperiments();

  return (
    <div className="panel overflow-x-auto">
      <table className="w-full min-w-[900px] border-collapse">
        <thead className="table-header">
          <tr>
            <th className="px-4 py-3">Experiment</th>
            <th className="px-4 py-3">Task</th>
            <th className="px-4 py-3">Policy</th>
            <th className="px-4 py-3">Episodes</th>
            <th className="px-4 py-3">Success</th>
            <th className="px-4 py-3">Created</th>
          </tr>
        </thead>
        <tbody>
          {experiments.map((experiment) => (
            <tr key={experiment.id}>
              <td className="table-cell font-medium text-graphite">{experiment.experiment_name}</td>
              <td className="table-cell">{experiment.task_name}</td>
              <td className="table-cell">{experiment.policy_name}:{experiment.policy_version}</td>
              <td className="table-cell">{experiment.num_episodes}</td>
              <td className="table-cell">{Math.round(experiment.success_rate * 100)}%</td>
              <td className="table-cell">{formatDateTime(experiment.created_at)}</td>
            </tr>
          ))}
          {experiments.length === 0 ? (
            <tr>
              <td colSpan={6} className="px-4 py-10 text-center text-sm text-slate-500">
                No experiments yet.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
