from __future__ import annotations

import numpy as np


class ScriptedPolicy:
    def __init__(self, action_dim: int = 4, gain: float = 0.9) -> None:
        self.action_dim = action_dim
        self.gain = gain

    def act(self, state: np.ndarray) -> np.ndarray:
        progress = float(state[0])
        action = np.zeros(self.action_dim, dtype=np.float32)
        action[0] = self.gain * (1.0 - progress)
        action[1] = 0.08 * np.sin(progress * np.pi)
        action[2] = -0.04 * progress
        action[3] = 0.03
        return action
