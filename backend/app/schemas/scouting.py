"""Scouting metrics and coaching brief schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ScoutingReportUpsert(BaseModel):
    """Raw match payloads to aggregate and save for an opponent."""

    opponent_team: str = Field(min_length=1, max_length=120)
    matches: list[dict[str, Any]]


class ScoutingReportResponse(BaseModel):
    """Persisted scouting metrics for an opponent."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    opponent_team: str
    metrics_json: dict[str, Any]
    ai_brief: str | None
    updated_at: datetime


class CoachBriefRequest(BaseModel):
    """Opponent selector for a brief grounded in a stored report."""

    opponent_team: str = Field(min_length=1, max_length=120)
    question: str = Field(default="Prepare a concise pre-match macro brief.", max_length=1000)


class CoachBriefResponse(BaseModel):
    """Grounded prompt text and the verified metrics used to create it."""

    opponent_team: str
    brief: str
    verified_metrics: dict[str, Any]