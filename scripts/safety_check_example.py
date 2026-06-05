from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robot.safety import SafetyChecker, SafetyConfig  # noqa: E402


def main() -> None:
    checker = SafetyChecker(SafetyConfig.default(action_dim=4, joint_dim=8))
    action_result = checker.prepare_action(np.array([0.5, -0.4, 0.05, 0.0], dtype=np.float32))
    observation_result = checker.validate_observation(
        joint_positions=np.zeros(8, dtype=np.float32),
        joint_velocities=np.zeros(8, dtype=np.float32),
        tcp_position=np.array([0.2, 0.0, 0.2], dtype=np.float32),
    )

    print(
        json.dumps(
            {
                "action_ok": action_result.ok,
                "action_violations": action_result.violations,
                "clipped_action": action_result.clipped_action.tolist()
                if action_result.clipped_action is not None
                else None,
                "observation_ok": observation_result.ok,
                "observation_violations": observation_result.violations,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
