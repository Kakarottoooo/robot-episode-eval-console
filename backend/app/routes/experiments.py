from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Experiment
from backend.app.schemas import ExperimentRead

router = APIRouter(prefix="/experiments", tags=["experiments"])


@router.get("", response_model=list[ExperimentRead])
def list_experiments(
    limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)
) -> list[Experiment]:
    return db.query(Experiment).order_by(Experiment.created_at.desc()).limit(limit).all()


@router.get("/{experiment_id}", response_model=ExperimentRead)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)) -> Experiment:
    experiment = db.query(Experiment).filter(Experiment.id == experiment_id).first()
    if experiment is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return experiment
