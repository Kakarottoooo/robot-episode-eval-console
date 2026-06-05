from __future__ import annotations

import unittest

import numpy as np

from robot.safety import SafetyChecker, SafetyConfig, WorkspaceBounds


class SafetyCheckerTests(unittest.TestCase):
    def test_prepare_action_clips_and_applies_low_speed_scale(self) -> None:
        checker = SafetyChecker(SafetyConfig.default(action_dim=4, joint_dim=4))

        result = checker.prepare_action(np.array([1.0, -1.0, 0.1, 0.0], dtype=np.float32))

        self.assertTrue(result.ok)
        self.assertIn("action_above_limit", result.violations)
        self.assertIn("action_below_limit", result.violations)
        np.testing.assert_allclose(
            result.clipped_action,
            np.array([0.125, -0.125, 0.05, 0.0], dtype=np.float32),
        )

    def test_emergency_stop_blocks_action(self) -> None:
        checker = SafetyChecker(SafetyConfig.default(action_dim=4, joint_dim=4))
        checker.set_emergency_stop(True)

        result = checker.prepare_action(np.zeros(4, dtype=np.float32))

        self.assertFalse(result.ok)
        self.assertEqual(result.violations, ["emergency_stop_active"])
        self.assertIsNone(result.clipped_action)

    def test_observation_reports_workspace_and_joint_violations(self) -> None:
        config = SafetyConfig(
            joint_lower_limits=(-1.0, -1.0),
            joint_upper_limits=(1.0, 1.0),
            action_lower_limits=(-0.2, -0.2),
            action_upper_limits=(0.2, 0.2),
            max_joint_velocity=0.5,
            workspace_bounds=WorkspaceBounds(min_xyz=(0.0, 0.0, 0.0), max_xyz=(1.0, 1.0, 1.0)),
        )
        checker = SafetyChecker(config)

        result = checker.validate_observation(
            joint_positions=np.array([0.0, 1.2], dtype=np.float32),
            joint_velocities=np.array([0.1, 0.7], dtype=np.float32),
            tcp_position=np.array([1.5, 0.0, 0.2], dtype=np.float32),
        )

        self.assertFalse(result.ok)
        self.assertIn("joint_position_above_limit", result.violations)
        self.assertIn("joint_velocity_above_limit", result.violations)
        self.assertIn("tcp_position_outside_workspace", result.violations)


if __name__ == "__main__":
    unittest.main()
