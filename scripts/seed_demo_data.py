from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.database import SessionLocal, init_db  # noqa: E402
from backend.app.services.evaluation_service import persist_evaluation_result  # noqa: E402
from robot.evaluation import run_mock_evaluation  # noqa: E402


DEMO_RUNS = [
    ("random_policy", "v1", 8, 11),
    ("scripted_policy", "v1", 8, 22),
    ("sac_baseline", "v1", 8, 33),
    ("sac_curriculum", "v2", 8, 44),
]


def main() -> None:
    init_db()
    with SessionLocal() as db:
        for policy_name, version, count, seed in DEMO_RUNS:
            result = run_mock_evaluation(
                task_name="pick_and_place_cube",
                policy_name=policy_name,
                policy_version=version,
                environment="simulation",
                num_episodes=count,
                seed=seed,
            )
            experiment = persist_evaluation_result(db, result)
            print(
                f"seeded {count} episodes for {policy_name}:{version} "
                f"(experiment id={experiment.id}, success={result.experiment['success_rate'] * 100:.1f}%)"
            )


if __name__ == "__main__":
    main()
