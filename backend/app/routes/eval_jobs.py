from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import EvaluationJob
from backend.app.schemas import EvalRunRequest, EvaluationJobRead
from backend.app.services.evaluation_service import run_evaluation_job

router = APIRouter(prefix="/eval", tags=["evaluation"])


@router.post("/run", response_model=EvaluationJobRead, status_code=202)
def run_eval(payload: EvalRunRequest, db: Session = Depends(get_db)) -> EvaluationJob:
    return run_evaluation_job(db, payload)


@router.get("/jobs", response_model=list[EvaluationJobRead])
def list_eval_jobs(
    limit: int = Query(default=50, ge=1, le=200), db: Session = Depends(get_db)
) -> list[EvaluationJob]:
    return db.query(EvaluationJob).order_by(EvaluationJob.started_at.desc()).limit(limit).all()


@router.get("/jobs/{job_id}", response_model=EvaluationJobRead)
def get_eval_job(job_id: str, db: Session = Depends(get_db)) -> EvaluationJob:
    job = db.query(EvaluationJob).filter(EvaluationJob.job_id == job_id).first()
    if job is None:
        raise HTTPException(status_code=404, detail="Evaluation job not found")
    return job
