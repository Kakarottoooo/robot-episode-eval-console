from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    import torch
    from torch.utils.data import Dataset
except ImportError:  # pragma: no cover - exercised when torch is not installed
    torch = None
    Dataset = object  # type: ignore


class RobotEpisodeDataset(Dataset):  # type: ignore[misc]
    def __init__(
        self,
        root_dir: str | Path,
        *,
        task_name: str | None = None,
        policy_name: str | None = None,
        success: bool | None = None,
    ) -> None:
        self.root_dir = Path(root_dir)
        self.episodes = []
        for metadata_path in sorted(self.root_dir.glob("episode_*/metadata.json")):
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            if task_name is not None and metadata.get("task_name") != task_name:
                continue
            if policy_name is not None and metadata.get("policy_name") != policy_name:
                continue
            if success is not None and bool(metadata.get("success")) != success:
                continue
            self.episodes.append((metadata_path.parent, metadata))

    def __len__(self) -> int:
        return len(self.episodes)

    def __getitem__(self, idx: int) -> dict[str, Any]:
        episode_dir, metadata = self.episodes[idx]
        states = np.load(episode_dir / "states.npy")
        actions = np.load(episode_dir / "actions.npy")
        rewards = np.load(episode_dir / "rewards.npy")
        timestamps = np.load(episode_dir / "timestamps.npy")

        if torch is not None:
            states = torch.from_numpy(states).float()
            actions = torch.from_numpy(actions).float()
            rewards = torch.from_numpy(rewards).float()
            timestamps = torch.from_numpy(timestamps).float()

        return {
            "states": states,
            "actions": actions,
            "rewards": rewards,
            "timestamps": timestamps,
            "metadata": metadata,
            "video_path": metadata.get("video_path"),
        }


def episode_collate_fn(batch: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "states": [item["states"] for item in batch],
        "actions": [item["actions"] for item in batch],
        "rewards": [item["rewards"] for item in batch],
        "timestamps": [item["timestamps"] for item in batch],
        "metadata": [item["metadata"] for item in batch],
        "video_path": [item["video_path"] for item in batch],
    }
