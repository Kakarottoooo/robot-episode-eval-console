from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from robot.envs import MockRobotEnv
from robot.policies import ExistingSACPolicy, RandomPolicy, ScriptedPolicy
from robot.recorder import EpisodeRecorder


@dataclass
class EvaluationResult:
    episodes: list[dict[str, object]]
    experiment: dict[str, object]


def run_mock_evaluation(
    *,
    task_name: str = "pick_and_place_cube",
    policy_name: str = "scripted_policy",
    policy_version: str = "v1",
    environment: str = "simulation",
    num_episodes: int = 20,
    data_root: str | Path | None = None,
    record_video: bool = False,
    seed: int | None = None,
) -> EvaluationResult:
    data_root = data_root or os.getenv("ROBOT_DATA_ROOT", "data/episodes")
    rng = np.random.default_rng(seed)
    recorder = EpisodeRecorder(root_dir=data_root, record_video=record_video)
    episodes: list[dict[str, object]] = []

    for _ in range(num_episodes):
        episode_seed = int(rng.integers(0, 2**31 - 1))
        env = MockRobotEnv(task_name=task_name, seed=episode_seed)
        policy = _make_policy(policy_name, env.action_dim, episode_seed)
        state = env.reset()
        episode_id = recorder.start_episode(
            task_name=task_name,
            policy_name=policy_name,
            policy_version=policy_version,
            environment=environment,
        )

        done = False
        info: dict[str, object] = {"success": False, "failure_reason": "timeout"}
        prev_action: np.ndarray | None = None
        jerk_values: list[float] = []
        collision_count = 0

        while not done:
            action = policy.act(state)
            next_state, reward, done, info = env.step(action)
            if bool(info.get("collision")):
                collision_count += 1
            if prev_action is not None:
                jerk_values.append(float(np.linalg.norm(action - prev_action)))
            prev_action = action.copy()
            timestamp = env.step_count * 0.05
            frame = env.render_frame() if record_video else None
            recorder.record_step(
                frame=frame,
                state=state,
                action=action,
                reward=reward,
                timestamp=timestamp,
            )
            state = next_state

        success = bool(info.get("success", False))
        metadata = recorder.end_episode(
            success=success,
            failure_reason=None if success else str(info.get("failure_reason") or "unknown"),
            duration_sec=env.step_count * 0.05,
            metrics={
                "collision_count": collision_count,
                "trajectory_jerk": float(np.mean(jerk_values)) if jerk_values else 0.0,
            },
        )
        metadata["episode_id"] = episode_id
        episodes.append(metadata)

    experiment = _summarize_experiment(
        episodes=episodes,
        task_name=task_name,
        policy_name=policy_name,
        policy_version=policy_version,
        environment=environment,
    )
    return EvaluationResult(episodes=episodes, experiment=experiment)


def _make_policy(policy_name: str, action_dim: int, seed: int) -> object:
    normalized = policy_name.lower()
    if "random" in normalized:
        return RandomPolicy(action_dim=action_dim, seed=seed)
    if "scripted" in normalized or "curriculum" in normalized:
        return ScriptedPolicy(action_dim=action_dim, gain=0.92)
    return ExistingSACPolicy(action_dim=action_dim)


def _summarize_experiment(
    *,
    episodes: list[dict[str, object]],
    task_name: str,
    policy_name: str,
    policy_version: str,
    environment: str,
) -> dict[str, object]:
    successes = [bool(episode["success"]) for episode in episodes]
    durations = [float(episode["duration_sec"]) for episode in episodes]
    collisions = [float(episode["collision_count"]) for episode in episodes]
    jerks = [float(episode["trajectory_jerk"]) for episode in episodes]
    now = datetime.now(timezone.utc)
    return {
        "experiment_name": f"{policy_name}_{policy_version}_{now.strftime('%Y%m%d_%H%M%S')}",
        "task_name": task_name,
        "policy_name": policy_name,
        "policy_version": policy_version,
        "environment": environment,
        "num_episodes": len(episodes),
        "success_rate": round(sum(successes) / max(len(successes), 1), 4),
        "avg_duration_sec": round(float(np.mean(durations)) if durations else 0.0, 4),
        "avg_collision_count": round(float(np.mean(collisions)) if collisions else 0.0, 4),
        "avg_trajectory_jerk": round(float(np.mean(jerks)) if jerks else 0.0, 4),
        "created_at": now,
    }
