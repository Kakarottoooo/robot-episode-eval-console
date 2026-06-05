from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.database import SessionLocal, init_db  # noqa: E402
from backend.app.services.evaluation_service import persist_evaluation_result  # noqa: E402
from robot.evaluation import run_mock_evaluation  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a mock robot evaluation.")
    parser.add_argument("--task", default="pick_and_place_cube")
    parser.add_argument("--policy", default="scripted_policy")
    parser.add_argument("--version", default="v1")
    parser.add_argument("--env", default="simulation", choices=["simulation", "real_robot"])
    parser.add_argument("--num_episodes", type=int, default=20)
    parser.add_argument("--record-video", action="store_true")
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    init_db()
    result = run_mock_evaluation(
        task_name=args.task,
        policy_name=args.policy,
        policy_version=args.version,
        environment=args.env,
        num_episodes=args.num_episodes,
        record_video=args.record_video,
        seed=args.seed,
    )
    with SessionLocal() as db:
        experiment = persist_evaluation_result(db, result)

    print(f"{len(result.episodes)} episodes saved")
    print(f"success rate: {result.experiment['success_rate'] * 100:.1f}%")
    print(f"avg duration: {result.experiment['avg_duration_sec']:.2f} sec")
    print(f"avg collision count: {result.experiment['avg_collision_count']:.2f}")
    print(f"avg trajectory jerk: {result.experiment['avg_trajectory_jerk']:.4f}")
    print(f"experiment saved to database with id={experiment.id}")


if __name__ == "__main__":
    main()
