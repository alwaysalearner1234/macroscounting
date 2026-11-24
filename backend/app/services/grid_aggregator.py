"""Pandas-based aggregation of match-level GRID-style telemetry."""

from collections.abc import Iterable
from typing import Any

import numpy as np
import pandas as pd

OBJECTIVES = ("dragon", "voidgrubs", "rift_herald", "baron")


def aggregate_matches(matches: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Compute macro indicators and map coordinates from normalized match payloads.

    Each match may contain ``teams`` (blue/red stats), ``events``, ``jungle_paths``,
    and ``wards``. Rates are returned as percentages in the 0–100 range.
    """
    rows = list(matches)
    if not rows:
        return _empty_metrics()

    team_rows: list[dict[str, Any]] = []
    focus_sides: dict[Any, str] = {}
    for match in rows:
        match_id = match.get("match_id")
        requested_side = str(match.get("focus_side", "blue")).casefold()
        side = requested_side if requested_side in ("blue", "red") else "blue"
        focus_sides[match_id] = side
        stats = match.get("teams", {}).get(side, {})
        team_rows.append({
            "match_id": match_id,
            "side": side,
            "gd15": _number(stats.get("gold_diff_at_15")),
            "first_blood": bool(stats.get("first_blood", False)),
            "first_tower": bool(stats.get("first_tower", False)),
            "win": bool(stats.get("won", False)),
        })
    teams = pd.DataFrame(team_rows)

    events = [
        {**event, "match_id": event.get("match_id", match.get("match_id"))}
        for match in rows
        for event in match.get("events", [])
    ]
    objective_rates: dict[str, float] = {}
    for objective in OBJECTIVES:
        first_event_by_match: dict[Any, dict[str, Any]] = {}
        matching_events = [event for event in events if str(event.get("type", "")).casefold() == objective]
        matching_events.sort(key=lambda event: _number(event.get("timestamp_seconds")))
        for event in matching_events:
            first_event_by_match.setdefault(event.get("match_id"), event)
        first_captures = sum(
            str(event.get("team", "")).casefold() == focus_sides.get(match_id, "blue")
            for match_id, event in first_event_by_match.items()
        )
        objective_rates[f"first_{objective}_capture_rate"] = round(
            100 * first_captures / len(rows), 2
        )

    path_coords = [
        {"match_id": match.get("match_id"), "team": side, "x": _number(point["x"]), "y": _number(point["y"]), "minute": _number(point.get("minute", 0))}
        for match in rows
        for side, points in match.get("jungle_paths", {}).items()
        for point in points
        if 0 <= _number(point.get("minute", 0)) <= 5 and "x" in point and "y" in point
    ]
    ward_coords = [
        {"match_id": match.get("match_id"), "team": str(ward.get("team", "unknown")), "x": _number(ward["x"]), "y": _number(ward["y"]), "objective": ward.get("objective")}
        for match in rows
        for ward in match.get("wards", [])
        if "x" in ward and "y" in ward and bool(ward.get("within_60s_of_objective", False))
    ]

    return {
        "matches": len(rows),
        "gd_at_15": round(float(teams["gd15"].mean()), 2) if not teams.empty else 0.0,
        "fb_rate": round(float(teams["first_blood"].mean() * 100), 2) if not teams.empty else 0.0,
        "ft_rate": round(float(teams["first_tower"].mean() * 100), 2) if not teams.empty else 0.0,
        "objective_capture_rates": objective_rates,
        "jungle_pathing_0_5": path_coords,
        "pre_objective_ward_coordinates": ward_coords,
        "win_rate": round(float(teams["win"].mean() * 100), 2) if not teams.empty else 0.0,
        "coordinate_bounds": {"x": [0, 15000], "y": [0, 15000]},
    }


def _number(value: Any) -> float:
    """Coerce a telemetry number to finite float, defaulting missing values to zero."""
    number = pd.to_numeric(value, errors="coerce")
    return float(number) if pd.notna(number) and np.isfinite(number) else 0.0


def _empty_metrics() -> dict[str, Any]:
    """Return the complete metric shape when no matches are available."""
    return {
        "matches": 0,
        "gd_at_15": 0.0,
        "fb_rate": 0.0,
        "ft_rate": 0.0,
        "objective_capture_rates": {f"first_{objective}_capture_rate": 0.0 for objective in OBJECTIVES},
        "jungle_pathing_0_5": [],
        "pre_objective_ward_coordinates": [],
        "win_rate": 0.0,
        "coordinate_bounds": {"x": [0, 15000], "y": [0, 15000]},
    }