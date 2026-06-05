from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.app.models import EvaluationJob, Experiment
from backend.app.schemas import EvalRunRequest
from backend.app.services.episode_service import upsert_episode
from robot.evaluation import EvaluationResult, run_mock_evaluation


def persist_evaluation_result(
    db: Session,
    result: EvaluationResult,
    *,
    experiment_name: str | None = None,
    commit: bool = True,
) -> Experiment:
    for episode in result.episodes:
        upsert_episode(db, episode)

    summary = result.experiment
    experiment = Experiment(
        experiment_name=experiment_name or summary["experiment_name"],
        task_name=summary["task_name"],
        policy_name=summary["policy_name"],
        policy_version=summary["policy_version"],
        environment=summary["environment"],
        num_episodes=summary["num_episodes"],
        success_rate=summary["success_rate"],
        avg_duration_sec=summary["avg_duration_sec"],
        avg_collision_count=summary["avg_collision_count"],
        avg_trajectory_jerk=summary["avg_trajectory_jerk"],
        created_at=summary["created_at"],
    )
    db.add(experiment)

    if commit:
        db.commit()
        db.refresh(experiment)
    return experiment


def run_evaluation_job(db: Session, request: EvalRunRequest) -> EvaluationJob:
    now = datetime.now(timezone.utc)
    job = EvaluationJob(
        job_id=f"eval_{uuid4().hex[:12]}",
        status="running",
        task_name=request.task_name,
        policy_name=request.policy_name,
        policy_version=request.policy_version,
        environment=request.environment,
        num_episodes=request.num_episodes,
        started_at=now,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        result = run_mock_evaluation(
            task_name=request.task_name,
            policy_name=request.policy_name,
            policy_version=request.policy_version,
            environment=request.environment,
            num_episodes=request.num_episodes,
        )
        persist_evaluation_result(
            db,
            result,
            experiment_name=f"{request.policy_name}_{request.policy_version}_{job.job_id}",
            commit=False,
        )
        job.status = "completed"
        job.finished_at = datetime.now(timezone.utc)
    except Exception as exc:  # pragma: no cover - surfaced through job status
        job.status = "failed"
        job.finished_at = datetime.now(timezone.utc)
        job.error_message = str(exc)

    db.commit()
    db.refresh(job)
    return job
