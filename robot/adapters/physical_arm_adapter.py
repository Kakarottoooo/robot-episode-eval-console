from __future__ import annotations

from dataclasses import dataclass
from time import monotonic

import numpy as np

from robot.safety import SafetyChecker, SafetyConfig, SafetyResult


@dataclass(frozen=True)
class PhysicalArmConfig:
    robot_type: str = "physical_arm"
    state_dim: int = 8
    action_dim: int = 4
    control_dt_sec: float = 0.05
    require_manual_reset: bool = True
    require_manual_label: bool = True


@dataclass
class RobotObservation:
    state: np.ndarray
    joint_positions: np.ndarray
    joint_velocities: np.ndarray
    tcp_position: np.ndarray | None
    timestamp: float
    frame: np.ndarray | None = None


@dataclass
class RobotStepResult:
    observation: RobotObservation
    reward: float
    done: bool
    info: dict[str, object]


class PhysicalArmAdapter:
    """Safety-first skeleton for real robot integration.

    This adapter intentionally does not talk to hardware yet. Hardware-specific
    subclasses should implement `_read_observation()` and `_send_action()`.
    """

    def __init__(
        self,
        config: PhysicalArmConfig | None = None,
        safety: SafetyChecker | None = None,
    ) -> None:
        self.config = config or PhysicalArmConfig()
        self.safety = safety or SafetyChecker(SafetyConfig.default(self.config.action_dim))
        self._started_at = monotonic()
        self._last_observation: RobotObservation | None = None
        self._closed = False

    @property
    def state_dim(self) -> int:
        return self.config.state_dim

    @property
    def action_dim(self) -> int:
        return self.config.action_dim

    def reset(self) -> np.ndarray:
        self._ensure_open()
        if self.config.require_manual_reset:
            self._wait_for_manual_reset()
        observation = self._read_observation()
        safety_result = self.safety.validate_observation(
            joint_positions=observation.joint_positions,
            joint_velocities=observation.joint_velocities,
            tcp_position=observation.tcp_position,
        )
        if not safety_result.ok:
            raise RuntimeError(f"Unsafe reset observation: {safety_result.violations}")
        self._last_observation = observation
        return observation.state.copy()

    def step(self, action: np.ndarray | list[float]) -> tuple[np.ndarray, float, bool, dict[str, object]]:
        self._ensure_open()
        prepared = self.safety.prepare_action(action)
        if not prepared.ok or prepared.clipped_action is None:
            return self._blocked_step(prepared)

        self._send_action(prepared.clipped_action)
        observation = self._read_observation()
        observation_safety = self.safety.validate_observation(
            joint_positions=observation.joint_positions,
            joint_velocities=observation.joint_velocities,
            tcp_position=observation.tcp_position,
        )
        self._last_observation = observation
        done = not observation_safety.ok
        reward = 0.0
        info: dict[str, object] = {
            "environment": "real_robot",
            "safety_ok": observation_safety.ok,
            "command_safety_violations": prepared.violations,
            "safety_violations": observation_safety.violations,
            "manual_label_required": self.config.require_manual_label,
        }
        return observation.state.copy(), reward, done, info

    def render_frame(self) -> np.ndarray | None:
        if self._last_observation is None:
            return None
        return self._last_observation.frame

    def close(self) -> None:
        self._closed = True

    def _read_observation(self) -> RobotObservation:
        raise NotImplementedError(
            "Implement camera/state reading in a hardware-specific subclass."
        )

    def _send_action(self, action: np.ndarray) -> None:
        raise NotImplementedError(
            "Implement command publishing in a hardware-specific subclass."
        )

    def _wait_for_manual_reset(self) -> None:
        # Real integrations should block on an operator confirmation channel.
        return None

    def _blocked_step(self, safety_result: SafetyResult) -> tuple[np.ndarray, float, bool, dict[str, object]]:
        state = (
            self._last_observation.state.copy()
            if self._last_observation is not None
            else np.zeros(self.config.state_dim, dtype=np.float32)
        )
        info: dict[str, object] = {
            "environment": "real_robot",
            "safety_ok": False,
            "safety_violations": safety_result.violations,
            "manual_label_required": self.config.require_manual_label,
        }
        return state, 0.0, True, info

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("PhysicalArmAdapter is closed.")
