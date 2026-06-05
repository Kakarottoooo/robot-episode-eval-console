from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class StepInfo:
    success: bool
    failure_reason: str | None
    collision: bool
    progress: float


class MockRobotEnv:
    """Small deterministic simulation stand-in for a robot manipulation task."""

    def __init__(
        self,
        task_name: str = "pick_and_place_cube",
        max_steps: int = 140,
        seed: int | None = None,
    ) -> None:
        self.task_name = task_name
        self.max_steps = max_steps
        self.rng = np.random.default_rng(seed)
        self.state_dim = 8
        self.action_dim = 4
        self.reset()

    def reset(self) -> np.ndarray:
        self.step_count = 0
        self.progress = float(self.rng.uniform(0.0, 0.08))
        self.collision_count = 0
        self.state = self.rng.normal(0.0, 0.05, size=self.state_dim).astype(np.float32)
        self.state[0] = self.progress
        return self.state.copy()

    def step(self, action: np.ndarray) -> tuple[np.ndarray, float, bool, dict[str, object]]:
        action = np.asarray(action, dtype=np.float32)
        self.step_count += 1

        control_quality = float(np.tanh(action[0]))
        action_norm = float(np.linalg.norm(action))
        collision = bool(self.rng.random() < max(0.01, (action_norm - 1.05) * 0.05))
        if collision:
            self.collision_count += 1

        drift = float(self.rng.normal(0.0, 0.006))
        self.progress = float(np.clip(self.progress + 0.008 + control_quality * 0.02 + drift, 0.0, 1.2))
        self.state = (
            0.92 * self.state
            + 0.08 * self.rng.normal(0.0, 1.0, size=self.state_dim)
            + 0.03 * np.pad(action, (0, self.state_dim - len(action)))
        ).astype(np.float32)
        self.state[0] = self.progress
        self.state[1] = self.collision_count

        success = self.progress >= 1.0 and self.collision_count <= 1
        timeout = self.step_count >= self.max_steps
        done = success or timeout or self.collision_count >= 5
        failure_reason = None
        if done and not success:
            if self.collision_count >= 5:
                failure_reason = "collision"
            elif self.progress < 0.35:
                failure_reason = "control_instability"
            elif self.progress < 0.85:
                failure_reason = "grasp_failure"
            else:
                failure_reason = "timeout"

        reward = self.progress - 0.06 * action_norm - 0.35 * int(collision)
        info = StepInfo(
            success=success,
            failure_reason=failure_reason,
            collision=collision,
            progress=self.progress,
        )
        return self.state.copy(), float(reward), done, info.__dict__

    def render_frame(self, width: int = 640, height: int = 360) -> np.ndarray:
        frame = np.full((height, width, 3), 246, dtype=np.uint8)
        track_y = height // 2
        frame[track_y - 8 : track_y + 8, 60 : width - 60] = np.array([210, 222, 232])
        x = int(60 + (width - 120) * min(self.progress, 1.0))
        frame[track_y - 34 : track_y + 34, x - 18 : x + 18] = np.array([20, 141, 153])
        if self.collision_count:
            frame[30:54, 30 : 30 + 28 * min(self.collision_count, 5)] = np.array([220, 38, 38])
        return frame
