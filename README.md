# robot-episode-eval-console

[![CI](https://github.com/Kakarottoooo/robot-episode-eval-console/actions/workflows/ci.yml/badge.svg)](https://github.com/Kakarottoooo/robot-episode-eval-console/actions/workflows/ci.yml)

An end-to-end Robot Episode Data Pipeline + Evaluation Console for recording robot episodes, storing structured metadata, running mock evaluation jobs, loading saved episodes with a PyTorch-style Dataset, and inspecting results in a web console.

The MVP uses a mock robot environment first. It also includes a safety-first physical robot adapter skeleton for future XLeRobot or manipulator integration without assuming hardware is available.

## Demo Screenshots

### Dashboard

![Dashboard](docs/screenshots/dashboard.png)

### Episodes

![Episodes](docs/screenshots/episodes.png)

### Episode Detail

![Episode Detail](docs/screenshots/episode-detail.png)

### Policy Comparison

![Policy Comparison](docs/screenshots/policy-comparison.png)

## Architecture

```text
Mock/XLeRobot/Physical Robot
  -> SafetyChecker + PhysicalArmAdapter
  -> EpisodeRecorder
  -> data/episodes/<episode_id>/{states,actions,rewards,timestamps,metadata}
  -> PostgreSQL metadata
  -> Evaluation metrics + experiments
  -> FastAPI backend
  -> Next.js Evaluation Console
  -> PyTorch Dataset/DataLoader utilities
```

## Quick Start

1. Start PostgreSQL with Docker Compose:

```powershell
docker compose up -d
```

2. Install Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
```

3. Copy environment settings:

```powershell
Copy-Item .env.example .env
```

The default PostgreSQL URL is:

```text
postgresql+psycopg://robot:robot@localhost:5432/robot_eval
```

4. Run the API from the repository root:

```powershell
uvicorn backend.app.main:app --reload
```

Open [http://localhost:8000/health](http://localhost:8000/health).

5. Seed demo data:

```powershell
python scripts\seed_demo_data.py
```

Or generate a specific evaluation run:

```powershell
python scripts\run_eval.py --task pick_and_place_cube --policy sac_baseline --version v1 --env simulation --num_episodes 20
```

6. Run the frontend:

```powershell
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## PostgreSQL Validation

The intended metadata store is PostgreSQL. SQLite is only a local fallback when `DATABASE_URL` is not set.

Start the database:

```powershell
docker compose up -d
docker compose ps
```

Seed demo data explicitly into PostgreSQL:

```powershell
$env:DATABASE_URL="postgresql+psycopg://robot:robot@localhost:5432/robot_eval"
$env:ROBOT_DATA_ROOT="data/episodes"
python scripts\seed_demo_data.py
```

Verify the rows are in PostgreSQL:

```powershell
docker exec robot_eval_postgres psql -U robot -d robot_eval -c "select count(*) as episodes from episodes; select count(*) as experiments from experiments;"
```

Expected demo result:

```text
episodes: 32
experiments: 4
```

You can also verify through the API:

```powershell
Invoke-RestMethod "http://localhost:8000/episodes?limit=1"
```

## API Examples

Create or upsert an episode metadata row:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/episodes -ContentType "application/json" -Body '{
  "episode_id": "episode_manual_001",
  "task_name": "pick_and_place_cube",
  "environment": "simulation",
  "robot_type": "xlerobot",
  "policy_name": "scripted_policy",
  "policy_version": "v1",
  "success": true,
  "duration_sec": 8.6,
  "num_steps": 86,
  "collision_count": 0,
  "trajectory_jerk": 0.12,
  "created_at": "2026-06-04T14:30:00Z"
}'
```

List episodes:

```powershell
Invoke-RestMethod http://localhost:8000/episodes
Invoke-RestMethod "http://localhost:8000/episodes?success=false&failure_reason=timeout"
```

Launch a mock evaluation job through the API:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/eval/run -ContentType "application/json" -Body '{
  "task_name": "pick_and_place_cube",
  "policy_name": "scripted_policy",
  "policy_version": "v1",
  "environment": "simulation",
  "num_episodes": 10
}'
```

## Data Format

Each episode is saved under `data/episodes/<episode_id>/`:

```text
metadata.json
states.npy
actions.npy
rewards.npy
timestamps.npy
video.mp4        optional, only when frames are recorded and OpenCV is installed
```

`metadata.json` contains task, robot, policy, success/failure labels, duration, step count, collision count, trajectory jerk, created timestamp, and paths to saved arrays.

## PyTorch Dataset

Install PyTorch if it is not already available in your Python environment:

```powershell
pip install torch
```

Run the example:

```powershell
python scripts\dataloader_example.py --root data\episodes --batch-size 2
```

The dataset supports filters for `task_name`, `policy_name`, and `success`. Episode trajectories can have different lengths, so the example uses a custom collate function.

## Continuous Integration

GitHub Actions runs two checks:

- Backend + PostgreSQL: installs Python dependencies, compiles backend/robot/scripts, runs safety tests, seeds demo data into a PostgreSQL service, and runs the DataLoader example.
- Frontend: installs dependencies with `npm ci`, audits production dependencies, typechecks, and builds the Next.js console.

Workflow file: `.github/workflows/ci.yml`.

## Current Phase

The MVP covers Phase 1 through Phase 6 and has started the Phase 7 hardware integration skeleton:

- FastAPI backend, Next.js frontend, PostgreSQL compose setup
- Episode metadata CRUD and episode detail API
- Episode recorder, mock robot environment, random/scripted/SAC-placeholder policies
- Evaluation metrics and experiment summaries
- Web console for dashboard, episodes, detail, and policy comparison
- PyTorch-compatible `RobotEpisodeDataset`, DataLoader example, and dataset export
- Safety-first `PhysicalArmAdapter` skeleton, safety checks, and manual episode labeling tool

Phase 7 is not connected to real hardware yet. The next milestone is implementing a hardware-specific adapter subclass with camera capture, state reading, command publishing, and 10 low-speed `real_robot` trials.

## Physical Robot Adapter Skeleton

The hardware-facing code starts with explicit safety gates:

```text
robot/adapters/physical_arm_adapter.py
robot/safety/checks.py
scripts/safety_check_example.py
scripts/label_episode.py
```

Run the safety example:

```powershell
python scripts\safety_check_example.py
```

Manually label an episode after a real-world or reviewed trial:

```powershell
python scripts\label_episode.py --episode-id episode_000001 --success false --failure-reason grasp_failure
```

Use `--require-db` when the label must also sync to PostgreSQL.

## Safety Notes for Physical Robots

Do not connect a real manipulator directly to the mock evaluation loop. Add a hardware adapter that enforces:

- joint limits
- velocity and acceleration limits
- torque/force limits when available
- workspace boundaries
- low-speed mode for first trials
- emergency stop access
- manual reset and success/failure labeling
- camera/state health checks

Start with simple tasks such as `move_to_target`, `pick_cube`, `place_cube`, `button_press`, and `object_push`.

## Resume Bullets

- Built an end-to-end robot learning data and evaluation platform that records synchronized robot states, actions, rewards, timestamps, success labels, failure reasons, and optional video into structured episode datasets with PostgreSQL metadata.
- Implemented a mock evaluation runner and PyTorch-compatible Dataset/DataLoader utilities for comparing policy variants across success rate, duration, collision count, trajectory jerk, and failure distribution.
- Built a Next.js + FastAPI evaluation console for filtering episodes, inspecting failures, comparing policies, and reviewing evaluation jobs.

More detail is in `docs/architecture.md`, `docs/data_schema.md`, `docs/hardware_setup.md`, and `docs/demo_plan.md`.
