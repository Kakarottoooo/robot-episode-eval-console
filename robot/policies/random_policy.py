from __future__ import annotations

import numpy as np


class RandomPolicy:
    def __init__(self, action_dim: int = 4, seed: int | None = None) -> None:
        self.action_dim = action_dim
        self.rng = np.random.default_rng(seed)

    def act(self, state: np.ndarray) -> np.ndarray:
        return self.rng.normal(0.0, 1.4, size=self.action_dim).astype(np.float32)
