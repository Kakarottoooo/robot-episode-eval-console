import type { EvaluationJob } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export function JobsTable({ jobs }: { jobs: EvaluationJob[] }) {
  return (
    <div className="panel overflow-x-auto">
      <div className="border-b border-line px-5 py-4">
        <h2 className="text-sm font-semibold text-graphite">Latest evaluation jobs</h2>
      </div>
      <table className="w-full min-w-[520px] border-collapse">
        <thead className="table-header">
          <tr>
            <th className="px-4 py-3">Job</th>
            <th className="px-4 py-3">Policy</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Started</th>
          </tr>
        </thead>
        <tbody>
          {jobs.map((job) => (
            <tr key={job.job_id}>
              <td className="table-cell font-medium text-graphite">{job.job_id}</td>
              <td className="table-cell">{job.policy_name}:{job.policy_version}</td>
              <td className="table-cell">
                <span className="rounded-md bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">
                  {job.status}
                </span>
              </td>
              <td className="table-cell">{job.started_at ? formatDateTime(job.started_at) : "queued"}</td>
            </tr>
          ))}
          {jobs.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-4 py-10 text-center text-sm text-slate-500">
                No jobs yet.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
