from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


class EpisodeRecorder:
    """Records one robot trial into the standard episode directory format."""

    def __init__(
        self,
        root_dir: str | Path = "data/episodes",
        robot_type: str = "xlerobot",
        record_video: bool = False,
    ) -> None:
        self.root_dir = Path(root_dir)
        self.robot_type = robot_type
        self.record_video = record_video
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self._reset_buffers()

    def start_episode(
        self,
        task_name: str,
        policy_name: str,
        environment: str,
        policy_version: str = "v1",
        episode_id: str | None = None,
    ) -> str:
        self._reset_buffers()
        self.episode_id = episode_id or self._next_episode_id()
        self.task_name = task_name
        self.policy_name = policy_name
        self.policy_version = policy_version
        self.environment = environment
        self.episode_dir = self.root_dir / self.episode_id
        self.episode_dir.mkdir(parents=True, exist_ok=False)
        self.created_at = datetime.now(timezone.utc)
        return self.episode_id

    def record_step(
        self,
        *,
        state: np.ndarray | list[float],
        action: np.ndarray | list[float],
        reward: float,
        timestamp: float,
        frame: np.ndarray | None = None,
    ) -> None:
        self.states.append(np.asarray(state, dtype=np.float32))
        self.actions.append(np.asarray(action, dtype=np.float32))
        self.rewards.append(float(reward))
        self.timestamps.append(float(timestamp))
        if frame is not None and self.record_video:
            self.frames.append(np.asarray(frame, dtype=np.uint8))

    def end_episode(
        self,
        *,
        success: bool,
        failure_reason: str | None,
        metrics: dict[str, Any] | None = None,
        duration_sec: float | None = None,
    ) -> dict[str, Any]:
        if self.episode_dir is None:
            raise RuntimeError("start_episode must be called before end_episode")

        metrics = metrics or {}
        states_path = self.episode_dir / "states.npy"
        actions_path = self.episode_dir / "actions.npy"
        rewards_path = self.episode_dir / "rewards.npy"
        timestamps_path = self.episode_dir / "timestamps.npy"

        np.save(states_path, np.asarray(self.states, dtype=np.float32))
        np.save(actions_path, np.asarray(self.actions, dtype=np.float32))
        np.save(rewards_path, np.asarray(self.rewards, dtype=np.float32))
        np.save(timestamps_path, np.asarray(self.timestamps, dtype=np.float32))

        video_path = self._write_video_if_possible()
        num_steps = len(self.rewards)
        if duration_sec is None:
            duration_sec = float(self.timestamps[-1]) if self.timestamps else 0.0

        metadata = {
            "episode_id": self.episode_id,
            "task_name": self.task_name,
            "environment": self.environment,
            "robot_type": self.robot_type,
            "policy_name": self.policy_name,
            "policy_version": self.policy_version,
            "success": bool(success),
            "failure_reason": None if success else failure_reason or "unknown",
            "duration_sec": round(float(duration_sec), 3),
            "num_steps": int(num_steps),
            "collision_count": int(metrics.get("collision_count", 0)),
            "trajectory_jerk": round(float(metrics.get("trajectory_jerk", 0.0)), 4),
            "video_path": video_path,
            "states_path": states_path.as_posix(),
            "actions_path": actions_path.as_posix(),
            "rewards_path": rewards_path.as_posix(),
            "timestamps_path": timestamps_path.as_posix(),
            "created_at": self.created_at.isoformat(),
        }

        metadata_path = self.episode_dir / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return metadata

    def _reset_buffers(self) -> None:
        self.episode_id: str | None = None
        self.episode_dir: Path | None = None
        self.task_name = ""
        self.policy_name = ""
        self.policy_version = ""
        self.environment = ""
        self.created_at = datetime.now(timezone.utc)
        self.states: list[np.ndarray] = []
        self.actions: list[np.ndarray] = []
        self.rewards: list[float] = []
        self.timestamps: list[float] = []
        self.frames: list[np.ndarray] = []

    def _next_episode_id(self) -> str:
        max_id = 0
        pattern = re.compile(r"episode_(\d{6})$")
        for path in self.root_dir.glob("episode_*"):
            match = pattern.match(path.name)
            if match:
                max_id = max(max_id, int(match.group(1)))
        return f"episode_{max_id + 1:06d}"

    def _write_video_if_possible(self) -> str | None:
        if not self.frames or self.episode_dir is None:
            return None
        try:
            import cv2  # type: ignore
        except ImportError:
            return None

        video_path = self.episode_dir / "video.mp4"
        height, width = self.frames[0].shape[:2]
        writer = cv2.VideoWriter(
            str(video_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            20.0,
            (width, height),
        )
        for frame in self.frames:
            writer.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        writer.release()
        return video_path.as_posix()
