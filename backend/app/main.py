from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.database import init_db
from backend.app.routes import episodes, eval_jobs, experiments

DATA_ROOT = Path(os.getenv("ROBOT_DATA_ROOT", "data/episodes"))
DATA_ROOT.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Robot Episode Evaluation API",
    version="0.1.0",
    description="Robot episode metadata, evaluation jobs, and experiment metrics.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "robot-episode-eval-api"}


app.mount("/media/episodes", StaticFiles(directory=DATA_ROOT), name="episode_media")
app.include_router(episodes.router)
app.include_router(experiments.router)
app.include_router(eval_jobs.router)
