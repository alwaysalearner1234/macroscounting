"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, coach, draft, scouting
from app.core.config import settings
from app.db.database import Base, engine
from app.db import models  # noqa: F401 - register ORM tables before create_all.


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create local starter tables when the API starts."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="C9 Draft & Scout API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(draft.router)
app.include_router(scouting.router)
app.include_router(coach.router)


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    """Return a lightweight liveness response for local orchestration."""
    return {"status": "ok"}