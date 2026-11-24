"""Persist verified opponent scouting metrics."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import ScoutingReport, User
from app.schemas.scouting import ScoutingReportResponse, ScoutingReportUpsert
from app.services.grid_aggregator import aggregate_matches

router = APIRouter(prefix="/scouting", tags=["scouting"])


@router.get("/reports", response_model=list[ScoutingReportResponse])
def list_reports(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[ScoutingReport]:
    """List the authenticated user's opponent reports."""
    return list(db.scalars(select(ScoutingReport).where(ScoutingReport.user_id == user.id)))


@router.put("/reports", response_model=ScoutingReportResponse)
def upsert_report(
    payload: ScoutingReportUpsert,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ScoutingReport:
    """Create or replace one user's verified aggregate for an opponent."""
    opponent = payload.opponent_team.strip()
    report = db.scalar(
        select(ScoutingReport).where(
            ScoutingReport.user_id == user.id, ScoutingReport.opponent_team == opponent
        )
    )
    if report is None:
        report = ScoutingReport(user_id=user.id, opponent_team=opponent)
        db.add(report)
    report.metrics_json = aggregate_matches(payload.matches)
    report.ai_brief = None
    db.commit()
    db.refresh(report)
    return report


@router.get("/reports/{opponent_team}", response_model=ScoutingReportResponse)
def get_report(
    opponent_team: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> ScoutingReport:
    """Fetch one report owned by the authenticated user."""
    report = db.scalar(
        select(ScoutingReport).where(
            ScoutingReport.user_id == user.id, ScoutingReport.opponent_team == opponent_team
        )
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Scouting report not found")
    return report