import type { Episode, Experiment } from "@/lib/api";

export type FailureRow = {
  reason: string;
  count: number;
};

export type PolicyRow = {
  policy: string;
  episodes: number;
  successRate: number;
  avgDuration: number;
  avgCollisions: number;
  avgJerk: number;
};

export function buildDashboardMetrics(episodes: Episode[], experiments: Experiment[]) {
  const totalEpisodes = episodes.length;
  const successes = episodes.filter((episode) => episode.success).length;
  const avgDuration =
    episodes.reduce((sum, episode) => sum + episode.duration_sec, 0) / Math.max(totalEpisodes, 1);

  return {
    totalEpisodes,
    totalExperiments: experiments.length,
    successRate: Math.round((successes / Math.max(totalEpisodes, 1)) * 100),
    avgDuration: avgDuration.toFixed(2),
  };
}

export function buildFailureDistribution(episodes: Episode[]): FailureRow[] {
  const counts = new Map<string, number>();
  episodes
    .filter((episode) => !episode.success)
    .forEach((episode) => {
      const reason = episode.failure_reason ?? "unknown";
      counts.set(reason, (counts.get(reason) ?? 0) + 1);
    });
  return Array.from(counts.entries())
    .map(([reason, count]) => ({ reason, count }))
    .sort((a, b) => b.count - a.count);
}

export function buildPolicyRows(experiments: Experiment[], episodes: Episode[]): PolicyRow[] {
  if (experiments.length > 0) {
    return experiments
      .map((experiment) => ({
        policy: `${experiment.policy_name}:${experiment.policy_version}`,
        episodes: experiment.num_episodes,
        successRate: experiment.success_rate,
        avgDuration: experiment.avg_duration_sec,
        avgCollisions: experiment.avg_collision_count,
        avgJerk: experiment.avg_trajectory_jerk,
      }))
      .sort((a, b) => b.successRate - a.successRate);
  }

  const groups = new Map<string, Episode[]>();
  episodes.forEach((episode) => {
    const key = `${episode.policy_name}:${episode.policy_version}`;
    groups.set(key, [...(groups.get(key) ?? []), episode]);
  });

  return Array.from(groups.entries()).map(([policy, group]) => ({
    policy,
    episodes: group.length,
    successRate: group.filter((episode) => episode.success).length / Math.max(group.length, 1),
    avgDuration: mean(group.map((episode) => episode.duration_sec)),
    avgCollisions: mean(group.map((episode) => episode.collision_count)),
    avgJerk: mean(group.map((episode) => episode.trajectory_jerk)),
  }));
}

function mean(values: number[]) {
  return values.reduce((sum, value) => sum + value, 0) / Math.max(values.length, 1);
}
