import Link from "next/link";
import type { Episode } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export function RecentEpisodes({ episodes }: { episodes: Episode[] }) {
  return (
    <div className="panel overflow-x-auto">
      <div className="flex items-center justify-between border-b border-line px-5 py-4">
        <h2 className="text-sm font-semibold text-graphite">Recent episodes</h2>
        <Link href="/episodes" className="text-sm font-medium text-teal hover:text-graphite">
          View all
        </Link>
      </div>
      <table className="w-full min-w-[560px] border-collapse">
        <thead className="table-header">
          <tr>
            <th className="px-4 py-3">Episode</th>
            <th className="px-4 py-3">Policy</th>
            <th className="px-4 py-3">Outcome</th>
            <th className="px-4 py-3">Created</th>
          </tr>
        </thead>
        <tbody>
          {episodes.map((episode) => (
            <tr key={episode.episode_id}>
              <td className="table-cell font-medium text-graphite">
                <Link href={`/episodes/${episode.episode_id}`} className="hover:text-teal">
                  {episode.episode_id}
                </Link>
              </td>
              <td className="table-cell">{episode.policy_name}</td>
              <td className="table-cell">
                <span className={`rounded-md px-2 py-1 text-xs font-medium ${
                  episode.success ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"
                }`}>
                  {episode.success ? "success" : "failed"}
                </span>
              </td>
              <td className="table-cell">{formatDateTime(episode.created_at)}</td>
            </tr>
          ))}
          {episodes.length === 0 ? (
            <tr>
              <td colSpan={4} className="px-4 py-10 text-center text-sm text-slate-500">
                No episodes yet.
              </td>
            </tr>
          ) : null}
        </tbody>
      </table>
    </div>
  );
}
