export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type Episode = {
  id: number;
  episode_id: string;
  task_name: string;
  environment: string;
  robot_type: string;
  policy_name: string;
  policy_version: string;
  success: boolean;
  failure_reason: string | null;
  duration_sec: number;
  num_steps: number;
  collision_count: number;
  trajectory_jerk: number;
  video_path: string | null;
  states_path: string | null;
  actions_path: string | null;
  rewards_path: string | null;
  timestamps_path: string | null;
  created_at: string;
};

export type Experiment = {
  id: number;
  experiment_name: string;
  task_name: string;
  policy_name: string;
  policy_version: string;
  environment: string;
  num_episodes: number;
  success_rate: number;
  avg_duration_sec: number;
  avg_collision_count: number;
  avg_trajectory_jerk: number;
  created_at: string;
};

export type EvaluationJob = {
  id: number;
  job_id: string;
  status: string;
  task_name: string;
  policy_name: string;
  policy_version: string;
  environment: string;
  num_episodes: number;
  started_at: string | null;
  finished_at: string | null;
  error_message: string | null;
};

export type EpisodeSeries = {
  episode_id: string;
  rewards: number[];
  timestamps: number[];
  state_norms: number[];
  action_norms: number[];
};

type EpisodeFilters = {
  success?: boolean;
  environment?: string;
  policy_name?: string;
  failure_reason?: string;
  limit?: number;
};

export async function getEpisodes(filters: EpisodeFilters = {}): Promise<Episode[]> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      params.set(key, String(value));
    }
  });
  return fetchJson<Episode[]>(`/episodes${params.size ? `?${params}` : ""}`, []);
}

export async function getEpisode(episodeId: string): Promise<Episode | null> {
  return fetchJson<Episode | null>(`/episodes/${episodeId}`, null);
}

export async function getEpisodeSeries(episodeId: string): Promise<EpisodeSeries | null> {
  return fetchJson<EpisodeSeries | null>(`/episodes/${episodeId}/series`, null);
}

export async function getExperiments(): Promise<Experiment[]> {
  return fetchJson<Experiment[]>("/experiments", []);
}

export async function getEvalJobs(): Promise<EvaluationJob[]> {
  return fetchJson<EvaluationJob[]>("/eval/jobs", []);
}

async function fetchJson<T>(path: string, fallback: T): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
    if (!response.ok) {
      return fallback;
    }
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}
