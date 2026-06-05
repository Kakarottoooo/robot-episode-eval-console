from __future__ import annotations

import numpy as np

from robot.policies.scripted_policy import ScriptedPolicy


class ExistingSACPolicy:
    """Adapter placeholder for loading a trained SAC policy later.

    MVP routes SAC-like policy names to a stable scripted controller so the
    data pipeline, evaluation loop, and UI can be exercised without model files.
    """

    def __init__(self, action_dim: int = 4) -> None:
        self._fallback = ScriptedPolicy(action_dim=action_dim, gain=0.72)

    def act(self, state: np.ndarray) -> np.ndarray:
        return self._fallback.act(state)
