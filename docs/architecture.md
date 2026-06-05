# Architecture

The MVP is built around a single episode contract shared by the recorder, database, evaluation scripts, API, and frontend.

```text
robot/env -> EpisodeRecorder -> data/episodes
                         \-> PostgreSQL episodes table
evaluation runner -> experiments table
FastAPI -> Next.js console
data/episodes -> RobotEpisodeDataset -> DataLoader
```

## Backend

The FastAPI service exposes:

- `GET /health`
- `POST /episodes`
- `GET /episodes`
- `GET /episodes/{episode_id}`
- `GET /episodes/{episode_id}/series`
- `PUT /episodes/{episode_id}`
- `DELETE /episodes/{episode_id}`
- `GET /experiments`
- `GET /experiments/{experiment_id}`
- `POST /eval/run`
- `GET /eval/jobs`
- `GET /eval/jobs/{job_id}`

SQLAlchemy owns the `episodes`, `experiments`, and `evaluation_jobs` tables. PostgreSQL is the intended database, with SQLite fallback for local smoke tests when `DATABASE_URL` is not set.

## Robot Layer

`EpisodeRecorder` is intentionally independent of the mock environment. A physical robot adapter should feed the same `record_step` calls with camera frames, robot state, actions, rewards, and timestamps.

## Frontend

The Next.js console is an operator/researcher tool with:

- dashboard metrics
- failure distribution
- latest jobs
- episode filtering
- episode detail and trajectory summaries
- policy comparison
