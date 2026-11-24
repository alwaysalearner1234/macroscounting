"""SQLAlchemy mappings for accounts, draft series, games, and scouting."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    """A locally authenticated or OAuth-linked account."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    oauth_provider: Mapped[str | None] = mapped_column(String(80))
    oauth_id: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    series: Mapped[list["Series"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    scouting_reports: Mapped[list["ScoutingReport"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Series(Base):
    """A Bo3/Bo5 draft series owned by a user."""

    __tablename__ = "series"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    team_blue: Mapped[str] = mapped_column(String(120), nullable=False)
    team_red: Mapped[str] = mapped_column(String(120), nullable=False)
    format: Mapped[str] = mapped_column(String(3), nullable=False)
    locked_champions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user: Mapped[User] = relationship(back_populates="series")
    games: Mapped[list["DraftGame"]] = relationship(
        back_populates="series", cascade="all, delete-orphan", order_by="DraftGame.game_number"
    )


class DraftGame(Base):
    """Ordered draft actions and optional winner for a single series game."""

    __tablename__ = "draft_games"
    __table_args__ = (UniqueConstraint("series_id", "game_number", name="uq_series_game_number"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    series_id: Mapped[int] = mapped_column(ForeignKey("series.id"), nullable=False, index=True)
    game_number: Mapped[int] = mapped_column(Integer, nullable=False)
    blue_bans: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    red_bans: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    blue_picks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    red_picks: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    winner: Mapped[str | None] = mapped_column(String(4))
    series: Mapped[Series] = relationship(back_populates="games")


class ScoutingReport(Base):
    """Stored opponent metrics and an optional grounded coaching brief."""

    __tablename__ = "scouting_reports"
    __table_args__ = (UniqueConstraint("user_id", "opponent_team", name="uq_user_opponent_report"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    opponent_team: Mapped[str] = mapped_column(String(120), nullable=False)
    metrics_json: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    ai_brief: Mapped[str | None] = mapped_column(String)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    user: Mapped[User] = relationship(back_populates="scouting_reports")