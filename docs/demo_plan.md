# Demo Plan

## Five-Minute Demo

1. Start PostgreSQL with `docker compose up -d`.
2. Start the API with `uvicorn backend.app.main:app --reload`.
3. Run `python scripts/seed_demo_data.py`.
4. Start the frontend with `npm run dev` from `frontend/`.
5. Open the dashboard and show total episodes, success rate, failures, and latest jobs.
6. Filter failed episodes on the Episodes page.
7. Open one episode detail page and review metadata, reward curve, state norm, and action norm.
8. Open Policy Comparison and compare success rate, collisions, duration, and jerk across policy variants.
9. Run `python scripts/dataloader_example.py --root data/episodes --batch-size 2`.

## What This Demonstrates

- robot data pipeline
- structured episode storage
- evaluation loop
- failure analysis
- researcher/operator UI
- reusable ML Dataset/DataLoader boundary
