from __future__ import annotations

from pathlib import Path

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models import Episode
from backend.app.schemas import EpisodeCreate, EpisodeRead, EpisodeSeries, EpisodeUpdate
from backend.app.services.episode_service import upsert_episode

router = APIRouter(prefix="/episodes", tags=["episodes"])


@router.post("", response_model=EpisodeRead, status_code=status.HTTP_201_CREATED)
def create_episode(payload: EpisodeCreate, db: Session = Depends(get_db)) -> Episode:
    return upsert_episode(db, payload.model_dump(), commit=True)


@router.get("", response_model=list[EpisodeRead])
def list_episodes(
    task_name: str | None = None,
    environment: str | None = None,
    policy_name: str | None = None,
    success: bool | None = None,
    failure_reason: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[Episode]:
    query = db.query(Episode)
    if task_name:
        query = query.filter(Episode.task_name == task_name)
    if environment:
        query = query.filter(Episode.environment == environment)
    if policy_name:
        query = query.filter(Episode.policy_name == policy_name)
    if success is not None:
        query = query.filter(Episode.success == success)
    if failure_reason:
        query = query.filter(Episode.failure_reason == failure_reason)

    return query.order_by(Episode.created_at.desc()).limit(limit).all()


@router.get("/{episode_id}/series", response_model=EpisodeSeries)
def get_episode_series(episode_id: str, db: Session = Depends(get_db)) -> EpisodeSeries:
    episode = _get_episode_or_404(db, episode_id)

    rewards = _load_vector(episode.rewards_path)
    timestamps = _load_vector(episode.timestamps_path)
    states = _load_matrix(episode.states_path)
    actions = _load_matrix(episode.actions_path)

    return EpisodeSeries(
        episode_id=episode.episode_id,
        rewards=rewards,
        timestamps=timestamps,
        state_norms=_row_norms(states),
        action_norms=_row_norms(actions),
    )


@router.get("/{episode_id}", response_model=EpisodeRead)
def get_episode(episode_id: str, db: Session = Depends(get_db)) -> Episode:
    return _get_episode_or_404(db, episode_id)


@router.put("/{episode_id}", response_model=EpisodeRead)
def update_episode(
    episode_id: str, payload: EpisodeUpdate, db: Session = Depends(get_db)
) -> Episode:
    episode = _get_episode_or_404(db, episode_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(episode, key, value)
    db.commit()
    db.refresh(episode)
    return episode


@router.delete("/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_episode(episode_id: str, db: Session = Depends(get_db)) -> Response:
    episode = _get_episode_or_404(db, episode_id)
    db.delete(episode)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _get_episode_or_404(db: Session, episode_id: str) -> Episode:
    episode = db.query(Episode).filter(Episode.episode_id == episode_id).first()
    if episode is None:
        raise HTTPException(status_code=404, detail="Episode not found")
    return episode


def _load_vector(path: str | None) -> list[float]:
    if not path or not Path(path).exists():
        return []
    values = np.load(path)
    return [float(value) for value in values.reshape(-1).tolist()]


def _load_matrix(path: str | None) -> np.ndarray:
    if not path or not Path(path).exists():
        return np.empty((0, 0), dtype=np.float32)
    values = np.load(path)
    if values.ndim == 1:
        return values.reshape(-1, 1)
    return values


def _row_norms(values: np.ndarray) -> list[float]:
    if values.size == 0:
        return []
    return [float(value) for value in np.linalg.norm(values, axis=1).tolist()]
