"""Series creation, draft actions, and game result endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import DraftGame, Series, User
from app.schemas.draft import DraftActionRequest, DraftActionResponse, GameResultRequest
from app.schemas.series import SeriesCreate, SeriesResponse
from app.services.fearless_engine import DRAFT_SEQUENCE, DraftRuleError, FearlessDraftEngine

router = APIRouter(prefix="/draft", tags=["draft"])


@router.post("/series", response_model=SeriesResponse, status_code=status.HTTP_201_CREATED)
def create_series(
    payload: SeriesCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> Series:
    """Create a Bo3/Bo5 series with no initial champion lockouts."""
    if payload.team_blue.strip().casefold() == payload.team_red.strip().casefold():
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Teams must be different")
    series = Series(
        user_id=user.id,
        team_blue=payload.team_blue.strip(),
        team_red=payload.team_red.strip(),
        format=payload.format,
        locked_champions=[],
    )
    db.add(series)
    db.commit()
    db.refresh(series)
    return series


@router.get("/series/{series_id}")
def get_series(
    series_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> dict:
    """Return owned series metadata, game actions, and reconstructed state."""
    series = _owned_series(series_id, db, user)
    engine = _rebuild_engine(series, db)
    return {
        "id": series.id,
        "team_blue": series.team_blue,
        "team_red": series.team_red,
        "format": series.format,
        "locked_champions": engine.locked_champions,
        "state": engine.state(),
        "games": [_game_payload(game) for game in series.games],
    }


@router.post("/series/{series_id}/actions", response_model=DraftActionResponse)
def submit_action(
    series_id: int,
    payload: DraftActionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> DraftActionResponse:
    """Apply the server's next required ban or pick to the current game."""
    series = _owned_series(series_id, db, user)
    engine = _rebuild_engine(series, db)
    try:
        action_type, team = engine.apply_action(payload.champion)
    except DraftRuleError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error

    game_number = engine.game_number
    game = db.scalar(
        select(DraftGame).where(DraftGame.series_id == series.id, DraftGame.game_number == game_number)
    )
    if game is None:
        game = DraftGame(series_id=series.id, game_number=game_number)
        db.add(game)
    target_field = f"{team}_{'bans' if action_type == 'ban' else 'picks'}"
    if game.id is None:
        game.blue_bans = []
        game.red_bans = []
        game.blue_picks = []
        game.red_picks = []
    getattr(game, target_field).append(payload.champion.strip())
    series.locked_champions = engine.locked_champions
    db.commit()
    return DraftActionResponse(
        game_number=game_number,
        action_index=engine.action_index,
        action_type=action_type,
        team=team,
        champion=payload.champion.strip(),
        draft_complete=engine.draft_complete,
        locked_champions=engine.locked_champions,
    )


@router.post("/series/{series_id}/games/{game_number}/result")
def record_game_result(
    series_id: int,
    game_number: int,
    payload: GameResultRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    """Finalize a fully drafted game, applying its picks to series lockouts."""
    series = _owned_series(series_id, db, user)
    engine = _rebuild_engine(series, db)
    if game_number != engine.game_number:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Game number is not current")
    try:
        engine.finalize_game(payload.winner)
    except DraftRuleError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    game = db.scalar(
        select(DraftGame).where(DraftGame.series_id == series.id, DraftGame.game_number == game_number)
    )
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Draft game not found")
    game.winner = payload.winner
    series.locked_champions = engine.locked_champions
    db.commit()
    return {"series_id": series.id, "state": engine.state()}


def _owned_series(series_id: int, db: Session, user: User) -> Series:
    """Load a series only when it belongs to the authenticated user."""
    series = db.scalar(select(Series).where(Series.id == series_id, Series.user_id == user.id))
    if series is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Series not found")
    return series


def _rebuild_engine(series: Series, db: Session) -> FearlessDraftEngine:
    """Replay persisted actions to reconstruct deterministic state after restarts."""
    games = list(
        db.scalars(
            select(DraftGame).where(DraftGame.series_id == series.id).order_by(DraftGame.game_number)
        )
    )
    completed: list[dict[str, object]] = []
    current: DraftGame | None = None
    for game in games:
        if game.winner is not None:
            completed.append({"picks": list(game.blue_picks) + list(game.red_picks), "winner": game.winner})
        else:
            current = game
    engine = FearlessDraftEngine(series_format=series.format, completed_games=completed)
    if current is not None:
        pools = {
            ("ban", "blue"): iter(current.blue_bans),
            ("ban", "red"): iter(current.red_bans),
            ("pick", "blue"): iter(current.blue_picks),
            ("pick", "red"): iter(current.red_picks),
        }
        for action_type, team in DRAFT_SEQUENCE:
            try:
                champion = next(pools[(action_type, team)])
            except StopIteration:
                break
            engine.apply_action(champion)
    return engine


def _game_payload(game: DraftGame) -> dict:
    """Serialize ORM game lists without exposing internal relationship objects."""
    return {
        "game_number": game.game_number,
        "blue_bans": game.blue_bans,
        "red_bans": game.red_bans,
        "blue_picks": game.blue_picks,
        "red_picks": game.red_picks,
        "winner": game.winner,
    }