"""Draft action and game-result schemas."""

from typing import Literal

from pydantic import BaseModel, Field


class DraftActionRequest(BaseModel):
    """Champion submitted for the server-determined next draft slot."""

    champion: str = Field(min_length=1, max_length=80)


class DraftActionResponse(BaseModel):
    """Accepted action and next draft slot."""

    game_number: int
    action_index: int
    action_type: Literal["ban", "pick"]
    team: Literal["blue", "red"]
    champion: str
    draft_complete: bool
    locked_champions: list[str]


class GameResultRequest(BaseModel):
    """Winner recorded after a game has been played."""

    winner: Literal["blue", "red"]