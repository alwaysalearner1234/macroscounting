"""Series creation and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SeriesCreate(BaseModel):
    """Input used to start a new draft series."""

    team_blue: str = Field(min_length=1, max_length=120)
    team_red: str = Field(min_length=1, max_length=120)
    format: Literal["Bo3", "Bo5"]


class SeriesResponse(BaseModel):
    """Series identity and current global fearless lockouts."""

    model_config = ConfigDict(from_attributes=True)
    id: int
    team_blue: str
    team_red: str
    format: Literal["Bo3", "Bo5"]
    locked_champions: list[str]
    created_at: datetime


class SeriesStateResponse(SeriesResponse):
    """Series response with game-level draft state."""

    games: list[dict]