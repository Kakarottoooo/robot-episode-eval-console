from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class WorkspaceBounds:
    min_xyz: tuple[float, float, float] = (-0.5, -0.5, 0.0)
    max_xyz: tuple[float, float, float] = (0.5, 0.5, 0.6)

    def contains(self, position: Sequence[float]) -> bool:
        values = np.asarray(position, dtype=np.float32)
        if values.shape != (3,):
            return False
        return bool(
            np.all(values >= np.asarray(self.min_xyz, dtype=np.float32))
            and np.all(values <= np.asarray(self.max_xyz, dtype=np.float32))
        )


@dataclass(frozen=True)
class SafetyConfig:
    joint_lower_limits: tuple[float, ...]
    joint_upper_limits: tuple[float, ...]
    action_lower_limits: tuple[float, ...]
    action_upper_limits: tuple[float, ...]
    max_joint_velocity: float = 0.5
    workspace_bounds: WorkspaceBounds = field(default_factory=WorkspaceBounds)
    low_speed_scale: float = 1.0

    @classmethod
    def default(cls, action_dim: int = 4, joint_dim: int = 8) -> SafetyConfig:
        return cls(
            joint_lower_limits=tuple([-3.14] * joint_dim),
            joint_upper_limits=tuple([3.14] * joint_dim),
            action_lower_limits=tuple([-0.25] * action_dim),
            action_upper_limits=tuple([0.25] * action_dim),
            max_joint_velocity=0.5,
            low_speed_scale=0.5,
        )


@dataclass
class SafetyResult:
    ok: bool
    violations: list[str]
    clipped_action: np.ndarray | None = None


class SafetyChecker:
    def __init__(self, config: SafetyConfig) -> None:
        self.config = config
        self.emergency_stop_active = False
        self._joint_lower = np.asarray(config.joint_lower_limits, dtype=np.float32)
        self._joint_upper = np.asarray(config.joint_upper_limits, dtype=np.float32)
        self._action_lower = np.asarray(config.action_lower_limits, dtype=np.float32)
        self._action_upper = np.asarray(config.action_upper_limits, dtype=np.float32)
        if self._joint_lower.shape != self._joint_upper.shape:
            raise ValueError("joint_lower_limits and joint_upper_limits must have the same shape")
        if self._action_lower.shape != self._action_upper.shape:
            raise ValueError("action_lower_limits and action_upper_limits must have the same shape")

    def set_emergency_stop(self, active: bool) -> None:
        self.emergency_stop_active = active

    def validate_observation(
        self,
        *,
        joint_positions: Sequence[float] | np.ndarray | None,
        joint_velocities: Sequence[float] | np.ndarray | None,
        tcp_position: Sequence[float] | np.ndarray | None,
    ) -> SafetyResult:
        violations: list[str] = []
        if self.emergency_stop_active:
            violations.append("emergency_stop_active")

        if joint_positions is not None:
            positions = np.asarray(joint_positions, dtype=np.float32)
            if positions.shape != self._joint_lower.shape:
                violations.append("joint_position_dimension_mismatch")
            else:
                if np.any(positions < self._joint_lower):
                    violations.append("joint_position_below_limit")
                if np.any(positions > self._joint_upper):
                    violations.append("joint_position_above_limit")

        if joint_velocities is not None:
            velocities = np.asarray(joint_velocities, dtype=np.float32)
            if velocities.shape != self._joint_lower.shape:
                violations.append("joint_velocity_dimension_mismatch")
            elif np.any(np.abs(velocities) > self.config.max_joint_velocity):
                violations.append("joint_velocity_above_limit")

        if tcp_position is not None and not self.config.workspace_bounds.contains(tcp_position):
            violations.append("tcp_position_outside_workspace")

        return SafetyResult(ok=not violations, violations=violations)

    def prepare_action(self, action: Sequence[float] | np.ndarray) -> SafetyResult:
        violations: list[str] = []
        if self.emergency_stop_active:
            return SafetyResult(ok=False, violations=["emergency_stop_active"])

        values = np.asarray(action, dtype=np.float32)
        if values.shape != self._action_lower.shape:
            return SafetyResult(ok=False, violations=["action_dimension_mismatch"])

        if np.any(values < self._action_lower):
            violations.append("action_below_limit")
        if np.any(values > self._action_upper):
            violations.append("action_above_limit")

        clipped = np.clip(values, self._action_lower, self._action_upper)
        clipped = clipped * float(self.config.low_speed_scale)
        return SafetyResult(ok=True, violations=violations, clipped_action=clipped)
