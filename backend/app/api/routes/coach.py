"""Grounded coaching prompt endpoint."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.database import get_db
from app.db.models import ScoutingReport, User
from app.schemas.scouting import CoachBriefRequest, CoachBriefResponse
from app.services.ai_coach import build_grounded_prompt

router = APIRouter(prefix="/coach", tags=["coach"])


@router.post("/brief", response_model=CoachBriefResponse)
def create_brief(
    payload: CoachBriefRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CoachBriefResponse:
    """Build a prompt using only the selected opponent's stored metrics."""
    report = db.scalar(
        select(ScoutingReport).where(
            ScoutingReport.user_id == user.id,
            ScoutingReport.opponent_team == payload.opponent_team.strip(),
        )
    )
    if report is None:
        raise HTTPException(status_code=404, detail="Verified scouting metrics are required first")
    metrics = report.metrics_json
    prompt = build_grounded_prompt(payload.question, metrics)
    return CoachBriefResponse(opponent_team=report.opponent_team, brief=prompt, verified_metrics=metrics)