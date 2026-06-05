from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FAILURE_REASONS = {
    "grasp_failure",
    "object_dropped",
    "collision",
    "timeout",
    "control_instability",
    "camera_or_state_error",
    "manual_stop",
    "unknown",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manually label a saved robot episode.")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--episode-id", help="Episode id under data/episodes, for example episode_000001")
    target.add_argument("--episode-dir", help="Path to an episode directory containing metadata.json")
    parser.add_argument("--root", default="data/episodes", help="Episode root used with --episode-id")
    parser.add_argument("--success", required=True, choices=["true", "false"])
    parser.add_argument("--failure-reason", choices=sorted(FAILURE_REASONS))
    parser.add_argument("--skip-db", action="store_true", help="Only update metadata.json")
    parser.add_argument("--require-db", action="store_true", help="Fail if database sync fails")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    episode_dir = Path(args.episode_dir) if args.episode_dir else Path(args.root) / args.episode_id
    metadata_path = episode_dir / "metadata.json"
    if not metadata_path.exists():
        raise SystemExit(f"metadata.json not found: {metadata_path}")

    success = args.success == "true"
    if not success and not args.failure_reason:
        raise SystemExit("--failure-reason is required when --success false")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["success"] = success
    metadata["failure_reason"] = None if success else args.failure_reason
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    db_status = "skipped"
    if not args.skip_db:
        try:
            from backend.app.database import SessionLocal, init_db
            from backend.app.services.episode_service import upsert_episode

            init_db()
            with SessionLocal() as db:
                upsert_episode(db, metadata, commit=True)
            db_status = "synced"
        except Exception as exc:
            db_status = f"failed: {exc}"
            if args.require_db:
                raise

    print(
        json.dumps(
            {
                "episode_id": metadata["episode_id"],
                "success": metadata["success"],
                "failure_reason": metadata["failure_reason"],
                "metadata_path": metadata_path.as_posix(),
                "database_sync": db_status,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
