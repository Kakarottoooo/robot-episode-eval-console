# Data Schema

## Episode Directory

```text
data/episodes/episode_000001/
  metadata.json
  states.npy
  actions.npy
  rewards.npy
  timestamps.npy
  video.mp4
```

`video.mp4` is optional. It is written only when frames are supplied and OpenCV is installed.

## metadata.json

```json
{
  "episode_id": "episode_000001",
  "task_name": "pick_and_place_cube",
  "environment": "simulation",
  "robot_type": "xlerobot",
  "policy_name": "scripted_policy",
  "policy_version": "v1",
  "success": true,
  "failure_reason": null,
  "duration_sec": 4.2,
  "num_steps": 84,
  "collision_count": 0,
  "trajectory_jerk": 0.12,
  "video_path": null,
  "states_path": "data/episodes/episode_000001/states.npy",
  "actions_path": "data/episodes/episode_000001/actions.npy",
  "rewards_path": "data/episodes/episode_000001/rewards.npy",
  "timestamps_path": "data/episodes/episode_000001/timestamps.npy",
  "created_at": "2026-06-04T14:30:00Z"
}
```

## Database Tables

`episodes` stores one row per trial. It indexes `episode_id`, `task_name`, `environment`, `policy_name`, `policy_version`, `success`, and `failure_reason`.

`experiments` stores aggregate evaluation summaries: episode count, success rate, duration, collisions, and jerk.

`evaluation_jobs` stores API-launched job status. The MVP runs jobs synchronously and records `completed` or `failed`.

## Failure Reasons

Use a controlled vocabulary:

- `grasp_failure`
- `object_dropped`
- `collision`
- `timeout`
- `control_instability`
- `camera_or_state_error`
- `manual_stop`
- `unknown`
