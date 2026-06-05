from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robot.datasets import RobotEpisodeDataset, episode_collate_fn  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load robot episodes with a PyTorch DataLoader.")
    parser.add_argument("--root", default="data/episodes")
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--task-name", default=None)
    parser.add_argument("--policy-name", default=None)
    parser.add_argument("--success", choices=["true", "false"], default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    success = None if args.success is None else args.success == "true"
    dataset = RobotEpisodeDataset(
        args.root,
        task_name=args.task_name,
        policy_name=args.policy_name,
        success=success,
    )
    print(f"dataset episodes: {len(dataset)}")
    if len(dataset) == 0:
        print("No episodes found. Run scripts/seed_demo_data.py first.")
        return

    try:
        from torch.utils.data import DataLoader
    except ImportError:
        sample = dataset[0]
        print("torch is not installed; loaded one sample without DataLoader.")
        print(f"episode_id: {sample['metadata']['episode_id']}")
        print(f"states shape: {sample['states'].shape}")
        print(f"actions shape: {sample['actions'].shape}")
        return

    loader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=False,
        collate_fn=episode_collate_fn,
    )
    batch = next(iter(loader))
    episode_ids = [item["episode_id"] for item in batch["metadata"]]
    print(f"batch episode_ids: {episode_ids}")
    print(f"first states shape: {tuple(batch['states'][0].shape)}")
    print(f"first actions shape: {tuple(batch['actions'][0].shape)}")
    print(f"first rewards shape: {tuple(batch['rewards'][0].shape)}")


if __name__ == "__main__":
    main()
