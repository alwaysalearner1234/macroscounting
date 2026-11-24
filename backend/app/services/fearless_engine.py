"""Deterministic Hard Fearless draft state machine for Bo3 and Bo5 series."""

from dataclasses import dataclass, field
from typing import Literal

Team = Literal["blue", "red"]
ActionType = Literal["ban", "pick"]
Winner = Literal["blue", "red"]

# Ten bans and ten picks, with the expected side and action fixed server-side.
DRAFT_SEQUENCE: tuple[tuple[ActionType, Team], ...] = (
    ("ban", "blue"), ("ban", "red"), ("ban", "blue"), ("ban", "red"),
    ("ban", "blue"), ("ban", "red"),
    ("pick", "blue"), ("pick", "red"), ("pick", "red"), ("pick", "blue"),
    ("pick", "blue"), ("pick", "red"),
    ("ban", "blue"), ("ban", "red"), ("ban", "red"), ("ban", "blue"),
    ("pick", "red"), ("pick", "blue"), ("pick", "blue"), ("pick", "red"),
)


class DraftRuleError(ValueError):
    """Raised when a draft action violates the current series state or rules."""


@dataclass
class FearlessDraftEngine:
    """Enforce per-game draft order and series-wide Hard Fearless lockouts."""

    series_format: Literal["Bo3", "Bo5"]
    completed_games: list[dict[str, object]] = field(default_factory=list)
    action_index: int = 0
    current_bans: list[str] = field(default_factory=list)
    current_picks: list[str] = field(default_factory=list)
    _locked_champions: set[str] = field(init=False, default_factory=set)
    _wins: dict[Team, int] = field(init=False, default_factory=lambda: {"blue": 0, "red": 0})
    series_complete: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        """Validate format and reconstruct wins/lockouts from completed games."""
        if self.series_format not in ("Bo3", "Bo5"):
            raise ValueError("Series format must be Bo3 or Bo5.")
        for game in self.completed_games:
            picks = game.get("picks", [])
            winner = game.get("winner")
            self._locked_champions.update(str(champion).casefold() for champion in picks)
            if winner in ("blue", "red"):
                self._wins[winner] += 1
        self.series_complete = self._has_series_winner() or len(self.completed_games) >= self.max_games

    @property
    def max_games(self) -> int:
        """Maximum games allowed by the selected format."""
        return 3 if self.series_format == "Bo3" else 5

    @property
    def games_to_win(self) -> int:
        """Wins needed to clinch the series."""
        return self.max_games // 2 + 1

    @property
    def game_number(self) -> int:
        """One-based game currently being drafted or played."""
        return len(self.completed_games) + 1

    @property
    def locked_champions(self) -> list[str]:
        """Return a stable display list of champions locked by prior picks."""
        return sorted(self._locked_champions)

    @property
    def draft_complete(self) -> bool:
        """Whether every draft action for the current game has been recorded."""
        return self.action_index == len(DRAFT_SEQUENCE)

    @property
    def next_action(self) -> tuple[ActionType, Team] | None:
        """The required next action, or ``None`` after the draft is complete."""
        if self.draft_complete or self.series_complete:
            return None
        return DRAFT_SEQUENCE[self.action_index]

    def apply_action(self, champion: str) -> tuple[ActionType, Team]:
        """Accept one champion in its required slot and return slot metadata."""
        if self.series_complete:
            raise DraftRuleError("The series is complete.")
        if self.draft_complete:
            raise DraftRuleError("The draft is complete; record the game result before continuing.")
        normalized = champion.strip().casefold()
        if not normalized:
            raise DraftRuleError("Champion name cannot be empty.")
        if normalized in {item.casefold() for item in self.current_bans + self.current_picks}:
            raise DraftRuleError(f"{champion} has already been used in this game.")
        action_type, team = DRAFT_SEQUENCE[self.action_index]
        if action_type == "pick" and normalized in self._locked_champions:
            raise DraftRuleError(f"{champion} is locked from a prior game in this series.")
        (self.current_bans if action_type == "ban" else self.current_picks).append(champion.strip())
        self.action_index += 1
        return action_type, team

    def finalize_game(self, winner: Winner) -> None:
        """Record a completed game's winner and lock every champion that was picked."""
        if self.series_complete:
            raise DraftRuleError("The series is complete.")
        if not self.draft_complete:
            raise DraftRuleError("All 20 draft actions are required before recording a result.")
        if winner not in ("blue", "red"):
            raise DraftRuleError("Winner must be blue or red.")
        self.completed_games.append({"picks": list(self.current_picks), "winner": winner})
        self._locked_champions.update(champion.casefold() for champion in self.current_picks)
        self._wins[winner] += 1
        self.series_complete = self._has_series_winner() or len(self.completed_games) >= self.max_games
        self.current_bans = []
        self.current_picks = []
        self.action_index = 0

    def state(self) -> dict[str, object]:
        """Return a JSON-ready snapshot of current progress and lockouts."""
        next_action = self.next_action
        return {
            "game_number": self.game_number,
            "action_index": self.action_index,
            "next_action": {"type": next_action[0], "team": next_action[1]} if next_action else None,
            "draft_complete": self.draft_complete,
            "series_complete": self.series_complete,
            "locked_champions": self.locked_champions,
            "wins": dict(self._wins),
        }

    def _has_series_winner(self) -> bool:
        return any(wins >= self.games_to_win for wins in self._wins.values())