# Coding and test guidelines

- Follow `CLAUDE.md` for architecture and the Hard Fearless rules; preserve service/router/schema separation.
- Use Python type hints, Pydantic request/response models, parameterized SQLAlchemy operations, and typed React components.
- Keep all API secrets configurable through environment variables. Never add real secrets to examples or source control.
- Draft behavior must remain deterministic. Add pytest coverage for normal series transitions, cross-team lockouts, invalid actions, and Bo3/Bo5 termination.
- For scouting changes, test metric definitions and missing/empty telemetry. Coach output must only cite metrics emitted by the aggregator.
- Run backend checks from `backend/`: `pytest` (and `uvicorn app.main:app` for a local API smoke test). Run frontend checks from `frontend/`: `npm run build`.
- Keep notebooks reproducible from the repository root and use the checked-in sample payload by default.