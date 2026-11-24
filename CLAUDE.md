# C9 Draft & Scout

Architecture and product source of truth for the Cloud9 x JetBrains hackathon prototype.

## Architecture

- `backend/` is a Python 3.12+ FastAPI application. Routers handle HTTP, Pydantic schemas validate the API boundary, services contain draft and scouting logic, and SQLAlchemy models persist data. SQLite is the local default; set `DATABASE_URL` to use another SQLAlchemy-supported database.
- `frontend/` is a Next.js App Router application using TypeScript and Tailwind CSS. Components are grouped by draft, scouting, and coaching responsibilities; `src/lib/api.ts` is the typed backend boundary.
- `data/` contains reproducible sample GRID-style match telemetry; `notebooks/` documents its exploration and metric export.
- `docker-compose.yml` runs the API and web application locally. Authentication uses stateless JWTs; no provider OAuth exchange or production LLM integration is configured in this starter.

## Conventions

- Keep HTTP concerns in `app/api/routes`, validation in `app/schemas`, persistence in `app/db`, and domain/data processing in `app/services`.
- Use type hints and concise docstrings for Python public interfaces. Keep React components typed, focused, and grouped by feature.
- Never trust client-provided scouting metrics as facts. Build coaching prompts from stored/verified aggregator output and label missing evidence rather than inventing it.
- Keep secrets in environment variables; `.env.example` and `.env.local.example` contain placeholders only. Do not commit credentials or generated databases.
- Add deterministic pytest coverage for state transitions, validation failures, and metric edge cases when changing domain behavior.

## Hard Fearless Draft rules

- A series is best-of-three or best-of-five. Each draft game uses a fixed 20-action sequence: 10 bans and 10 picks split evenly between blue and red, with the expected side/action enforced by the server.
- Champion names are unique within a game. A champion picked in any completed game is locked for the remainder of that series and cannot be picked by either team in later games. Previously picked champions remain legal ban targets; bans do not create lockouts.
- A lockout only becomes permanent when a draft is finalized with a game winner. Incomplete drafts do not contaminate later games. The series ends when a side reaches the required wins or the format's maximum games is reached.
- This rule is intentionally series-scoped; champions are available again in a new series.

## Database schema

- `users`: `id`, unique `email`, `hashed_password`, nullable `oauth_provider`/`oauth_id`, `created_at`.
- `series`: `id`, `user_id`, `team_blue`, `team_red`, `format` (`Bo3`/`Bo5`), JSON `locked_champions`, `created_at`.
- `draft_games`: `id`, `series_id`, `game_number`, JSON blue/red bans and picks, nullable `winner`.
- `scouting_reports`: `id`, `user_id`, `opponent_team`, JSON `metrics_json`, nullable `ai_brief`, `updated_at`.

## Local run commands

From the repository root, copy `.env.example` to `.env`, then run:

```powershell
docker compose up --build
```

The API is at `http://localhost:8000` and its OpenAPI page is `http://localhost:8000/docs`; the UI is at `http://localhost:3000`.

For direct development, create a Python 3.12+ environment and install `backend/requirements.txt`. From `backend/`, set `$env:DATABASE_URL = 'sqlite:///./c9_draft_scout.db'` and run `uvicorn app.main:app --reload`. In another terminal run `npm install` and `npm run dev` from `frontend/`. Copy `frontend/.env.local.example` to `.env.local` if the API URL differs from its default. Run backend tests from `backend/` with `pytest`.