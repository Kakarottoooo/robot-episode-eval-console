import Link from "next/link";
import { CheckCircle2, CircleX } from "lucide-react";
import type { Episode } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export function EpisodeTable({ episodes }: { episodes: Episode[] }) {
  return (
    <div className="panel overflow-x-auto">
      <table className="w-full min-w-[1040px] border-collapse">
        <thead className="table-header">
          <tr>
            <th className="px-4 py-3">Episode</th>
            <th className="px-4 py-3">Task</th>
            <th className="px-4 py-3">Environment</th>
            <th className="px-4 py-3">Policy</th>
            <th className="px-4 py-3">Outcome</th>
            <th className="px-4 py-3">Failure</th>
            <th className="px-4 py-3">Duration</th>
            <th className="px-4 py-3">Created</th>
          </tr>
        </thead>
        <tbody>
          {episodes.map((episode) => (
            <tr key={episode.episode_id} className="hover:bg-slate-50">
              <td className="table-cell font-medium text-graphite">
                <Link href={`/episodes/${episode.episode_id}`} className="hover:text-teal">
                  {episode.episode_id}
                </Link>
              </td>
              <td className="table-cell">{episode.task_name}</td>
              <td className="table-cell">{episode.environment}</td>
              <td className="table-cell">{episode.policy_name}:{episode.policy_version}</td>
              <td className="table-cell">
                <span className={`inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium ${
                  episode.success ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"
                }`}>
                  {episode.success ? <CheckCircle2 size={14} /> : <CircleX size={14} />}
                  {episode.success ? "success" : "failed"}
                </span>
              </td>
              <td className="table-cell">{episode.failure_reason ?? "none"}</td>
              <td className="table-cell">{episode.duration_sec.toFixed(2)}s</td>
              <td className="table-cell">{formatDateTime(episode.created_at)}</td>
            </tr>
          ))}
          {episodes.length === 0 ? (
            <tr>
              <td colSpan={8} className="px-4 py-10 text-center text-sm text-slate-500">
                No episodes match the current filters.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
