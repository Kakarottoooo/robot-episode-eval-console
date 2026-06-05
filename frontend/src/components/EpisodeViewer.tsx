import type { Episode, EpisodeSeries } from "@/lib/api";
import { API_BASE_URL } from "@/lib/api";
import { formatDateTime } from "@/lib/format";

export function EpisodeViewer({
  episode,
  series,
}: {
  episode: Episode;
  series: EpisodeSeries | null;
}) {
  const videoUrl = episode.video_path
    ? `${API_BASE_URL}/media/episodes/${episode.episode_id}/video.mp4`
    : null;

  return (
    <div className="grid gap-5 xl:grid-cols-[1fr_360px]">
      <section className="space-y-5">
        <div className="panel overflow-hidden">
          <div className="border-b border-line px-5 py-4">
            <h2 className="text-base font-semibold text-graphite">{episode.episode_id}</h2>
            <p className="text-sm text-slate-500">{episode.task_name} · {episode.policy_name}:{episode.policy_version}</p>
          </div>
          <div className="bg-slate-950 p-4">
            {videoUrl ? (
              <video className="aspect-video w-full rounded-md bg-black" controls src={videoUrl} />
            ) : (
              <div className="flex aspect-video items-center justify-center rounded-md border border-slate-800 bg-slate-900 text-sm text-slate-400">
                No video recorded for this episode
              </div>
            )}
          </div>
        </div>

        <TrajectoryPanel title="Reward curve" values={series?.rewards ?? []} tone="teal" />
        <div className="grid gap-5 md:grid-cols-2">
          <TrajectoryPanel title="State norm" values={series?.state_norms ?? []} tone="cyan" />
          <TrajectoryPanel title="Action norm" values={series?.action_norms ?? []} tone="amber" />
        </div>
      </section>

      <aside className="panel h-fit p-5">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-graphite">Metadata</h3>
          <span className={`rounded-md px-2 py-1 text-xs font-medium ${
            episode.success ? "bg-emerald-50 text-emerald-700" : "bg-red-50 text-red-700"
          }`}>
            {episode.success ? "success" : "failed"}
          </span>
        </div>
        <dl className="space-y-3 text-sm">
          <Meta label="Environment" value={episode.environment} />
          <Meta label="Robot" value={episode.robot_type} />
          <Meta label="Failure" value={episode.failure_reason ?? "none"} />
          <Meta label="Steps" value={episode.num_steps.toString()} />
          <Meta label="Duration" value={`${episode.duration_sec.toFixed(2)}s`} />
          <Meta label="Collisions" value={episode.collision_count.toString()} />
          <Meta label="Trajectory jerk" value={episode.trajectory_jerk.toFixed(4)} />
          <Meta label="Created" value={formatDateTime(episode.created_at)} />
        </dl>
      </aside>
    </div>
  );
}

function Meta({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-3 border-b border-slate-100 pb-2">
      <dt className="text-slate-500">{label}</dt>
      <dd className="text-right font-medium text-slate-800">{value}</dd>
    </div>
  );
}

function TrajectoryPanel({
  title,
  values,
  tone,
}: {
  title: string;
  values: number[];
  tone: "teal" | "cyan" | "amber";
}) {
  const color = tone === "teal" ? "#0f8b8d" : tone === "cyan" ? "#00a3b5" : "#d97706";
  const width = 720;
  const height = 180;
  const points = buildPoints(values, width, height);

  return (
    <div className="panel p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-graphite">{title}</h3>
        <span className="text-xs text-slate-500">{values.length} samples</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="h-44 w-full rounded-md bg-slate-50">
        <path d={`M 0 ${height - 24} H ${width}`} stroke="#d8e0e8" strokeWidth="1" />
        {points ? <polyline fill="none" stroke={color} strokeWidth="3" points={points} /> : null}
      </svg>
    </div>
  );
}

function buildPoints(values: number[], width: number, height: number) {
  if (values.length < 2) {
    return "";
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = height - 20 - ((value - min) / range) * (height - 40);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}
