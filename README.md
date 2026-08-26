https://nonprofit-intel-ten.vercel.app/

# Nonprofit Intelligence Platform

A financial research and discovery platform for the nonprofit sector,
built from public IRS Form 990 data.

## Why

Nonprofits disclose substantial financial information publicly, but the
raw filings are built for regulatory compliance, not exploration. This
platform turns them into searchable longitudinal data: growth analysis,
funding structure, peer benchmarking, and discovery.

## Architecture

Next.js (Vercel) → FastAPI → PostgreSQL
                     ↑
          Python ETL pipeline ← IRS 990 datasets

## Status

- [x] Stage 0: scaffolding, Docker, CI
- [x] Stage 1: prototype on ProPublica API
- [ ] Stage 2: own ingestion pipeline (CA)
- [ ] Stage 3: analytics + rankings
- [ ] Stage 4: peer benchmarking
- [ ] Stage 5: semantic discovery

## Running locally

docker compose up --build   # backend + postgres
cd frontend; npm run dev    # frontend on :3000

## Screenshots

<img width="960" height="600" alt="image" src="https://github.com/user-attachments/assets/2e52cd9b-3ccb-43a7-a570-188ac0a3d896" />

<img width="960" height="600" alt="image" src="https://github.com/user-attachments/assets/1e3bf748-fe23-4a4f-ae81-ad582a5acfd1" />
