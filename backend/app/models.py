from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from backend.app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Episode(Base):
    __tablename__ = "episodes"

    id = Column(Integer, primary_key=True, index=True)
    episode_id = Column(String(128), unique=True, index=True, nullable=False)
    task_name = Column(String(128), index=True, nullable=False)
    environment = Column(String(64), index=True, nullable=False)
    robot_type = Column(String(64), nullable=False)
    policy_name = Column(String(128), index=True, nullable=False)
    policy_version = Column(String(64), index=True, nullable=False)
    success = Column(Boolean, index=True, nullable=False, default=False)
    failure_reason = Column(String(128), index=True, nullable=True)
    duration_sec = Column(Float, nullable=False, default=0.0)
    num_steps = Column(Integer, nullable=False, default=0)
    collision_count = Column(Integer, nullable=False, default=0)
    trajectory_jerk = Column(Float, nullable=False, default=0.0)
    video_path = Column(Text, nullable=True)
    states_path = Column(Text, nullable=True)
    actions_path = Column(Text, nullable=True)
    rewards_path = Column(Text, nullable=True)
    timestamps_path = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    experiment_name = Column(String(160), nullable=False)
    task_name = Column(String(128), index=True, nullable=False)
    policy_name = Column(String(128), index=True, nullable=False)
    policy_version = Column(String(64), index=True, nullable=False)
    environment = Column(String(64), index=True, nullable=False)
    num_episodes = Column(Integer, nullable=False, default=0)
    success_rate = Column(Float, nullable=False, default=0.0)
    avg_duration_sec = Column(Float, nullable=False, default=0.0)
    avg_collision_count = Column(Float, nullable=False, default=0.0)
    avg_trajectory_jerk = Column(Float, nullable=False, default=0.0)
    created_at = Column(DateTime(timezone=True), nullable=False, default=utc_now)


class EvaluationJob(Base):
    __tablename__ = "evaluation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(128), unique=True, index=True, nullable=False)
    status = Column(String(32), index=True, nullable=False, default="queued")
    task_name = Column(String(128), index=True, nullable=False)
    policy_name = Column(String(128), index=True, nullable=False)
    policy_version = Column(String(64), index=True, nullable=False)
    environment = Column(String(64), index=True, nullable=False)
    num_episodes = Column(Integer, nullable=False, default=0)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
