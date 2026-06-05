from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EpisodeBase(BaseModel):
    episode_id: str
    task_name: str
    environment: str = "simulation"
    robot_type: str = "xlerobot"
    policy_name: str
    policy_version: str = "v1"
    success: bool
    failure_reason: str | None = None
    duration_sec: float = 0.0
    num_steps: int = 0
    collision_count: int = 0
    trajectory_jerk: float = 0.0
    video_path: str | None = None
    states_path: str | None = None
    actions_path: str | None = None
    rewards_path: str | None = None
    timestamps_path: str | None = None
    created_at: datetime | None = None


class EpisodeCreate(EpisodeBase):
    pass


class EpisodeUpdate(BaseModel):
    task_name: str | None = None
    environment: str | None = None
    robot_type: str | None = None
    policy_name: str | None = None
    policy_version: str | None = None
    success: bool | None = None
    failure_reason: str | None = None
    duration_sec: float | None = None
    num_steps: int | None = None
    collision_count: int | None = None
    trajectory_jerk: float | None = None
    video_path: str | None = None
    states_path: str | None = None
    actions_path: str | None = None
    rewards_path: str | None = None
    timestamps_path: str | None = None
    created_at: datetime | None = None


class EpisodeRead(EpisodeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


class EpisodeSeries(BaseModel):
    episode_id: str
    rewards: list[float]
    timestamps: list[float]
    state_norms: list[float]
    action_norms: list[float]


class ExperimentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    experiment_name: str
    task_name: str
    policy_name: str
    policy_version: str
    environment: str
    num_episodes: int
    success_rate: float
    avg_duration_sec: float
    avg_collision_count: float
    avg_trajectory_jerk: float
    created_at: datetime


class EvalRunRequest(BaseModel):
    task_name: str = "pick_and_place_cube"
    policy_name: str = "scripted_policy"
    policy_version: str = "v1"
    environment: str = "simulation"
    num_episodes: int = Field(default=10, ge=1, le=200)


class EvaluationJobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: str
    status: str
    task_name: str
    policy_name: str
    policy_version: str
    environment: str
    num_episodes: int
    started_at: datetime | None = None
    finished_at: datetime | None = None
    error_message: str | None = None
