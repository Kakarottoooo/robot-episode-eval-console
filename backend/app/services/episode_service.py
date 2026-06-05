from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from backend.app.models import Episode


def _coerce_created_at(value: Any) -> Any:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, str):
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    return value


def upsert_episode(db: Session, data: dict[str, Any], *, commit: bool = False) -> Episode:
    payload = dict(data)
    payload["created_at"] = _coerce_created_at(payload.get("created_at"))

    episode = db.query(Episode).filter(Episode.episode_id == payload["episode_id"]).first()
    if episode is None:
        episode = Episode(**payload)
        db.add(episode)
    else:
        for key, value in payload.items():
            setattr(episode, key, value)

    if commit:
        db.commit()
        db.refresh(episode)
    return episode
