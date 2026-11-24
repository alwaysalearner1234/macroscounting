"""Regression tests for Hard Fearless lockouts and series transitions."""

import pytest

from app.services.fearless_engine import DRAFT_SEQUENCE, DraftRuleError, FearlessDraftEngine


def complete_draft(engine: FearlessDraftEngine, prefix: str = "Champ") -> list[str]:
    """Fill every slot with unique predictable champions and return picked names."""
    picked = []
    for index in range(engine.action_index, len(DRAFT_SEQUENCE)):
        action_type, _ = DRAFT_SEQUENCE[index]
        champion = f"{prefix}{index}"
        expected, _ = engine.apply_action(champion)
        assert expected == action_type
        if action_type == "pick":
            picked.append(champion)
    return picked


@pytest.mark.parametrize("series_format,max_games", [("Bo3", 3), ("Bo5", 5)])
def test_format_transitions_and_series_win(series_format: str, max_games: int) -> None:
    engine = FearlessDraftEngine(series_format=series_format)  # type: ignore[arg-type]
    picks = complete_draft(engine)
    assert engine.draft_complete
    engine.finalize_game("blue")
    assert engine.game_number == 2
    assert engine.locked_champions == sorted(champion.casefold() for champion in picks)
    for index in range(6):
        engine.apply_action(f"NextBan{index}")
    with pytest.raises(DraftRuleError, match="locked"):
        engine.apply_action(picks[0])

    complete_draft(engine, "Next")
    engine.finalize_game("blue")
    assert len(engine.completed_games) == 2
    assert engine.series_complete == (series_format == "Bo3")
    if series_format == "Bo5":
        complete_draft(engine, "Decider")
        engine.finalize_game("blue")
        assert engine.series_complete
    assert engine.max_games == max_games


def test_bans_may_target_locked_champions_but_picks_may_not() -> None:
    first = FearlessDraftEngine(series_format="Bo3")
    picks = complete_draft(first)
    first.finalize_game("red")

    next_game = FearlessDraftEngine(series_format="Bo3", completed_games=first.completed_games)
    assert next_game.apply_action(picks[0]) == ("ban", "blue")
    next_game.apply_action("AnotherBan")
    next_game.apply_action("ThirdBan")
    next_game.apply_action("FourthBan")
    next_game.apply_action("FifthBan")
    next_game.apply_action("SixthBan")
    with pytest.raises(DraftRuleError, match="locked"):
        next_game.apply_action(picks[0])


def test_repeated_champion_and_early_result_are_rejected() -> None:
    engine = FearlessDraftEngine(series_format="Bo5")
    engine.apply_action("Shared")
    with pytest.raises(DraftRuleError, match="already been used"):
        engine.apply_action("Shared")
    with pytest.raises(DraftRuleError, match="20 draft actions"):
        engine.finalize_game("blue")


def test_incomplete_game_does_not_create_series_lockouts() -> None:
    engine = FearlessDraftEngine(series_format="Bo3")
    for index in range(6):
        engine.apply_action(f"Ban{index}")
    engine.apply_action("UnfinishedPick")

    assert engine.locked_champions == []
    with pytest.raises(DraftRuleError, match="20 draft actions"):
        engine.finalize_game("blue")


def test_bo5_series_can_reach_fifth_game_and_lock_all_prior_picks() -> None:
    engine = FearlessDraftEngine(series_format="Bo5")
    for game_number in range(1, 6):
        complete_draft(engine, f"Game{game_number}Champ")
        engine.finalize_game("blue" if game_number % 2 else "red")
    assert engine.series_complete
    assert engine.game_number == 6
    assert len(engine.locked_champions) == 50


def test_cannot_draft_after_series_is_won() -> None:
    engine = FearlessDraftEngine(series_format="Bo3")
    for game_number in range(1, 3):
        complete_draft(engine, f"Game{game_number}Champ")
        engine.finalize_game("red")
    with pytest.raises(DraftRuleError, match="series is complete"):
        engine.apply_action("NewChampion")