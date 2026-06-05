from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from robot.datasets import RobotEpisodeDataset  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a filtered episode manifest.")
    parser.add_argument("--root", default="data/episodes")
    parser.add_argument("--out", default="data/exports/dataset_manifest.json")
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
    manifest = [metadata for _, metadata in dataset.episodes]
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"exported {len(manifest)} episodes to {out_path}")


if __name__ == "__main__":
    main()
