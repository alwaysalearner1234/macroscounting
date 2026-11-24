"""Metric coverage for the sample GRID-style telemetry contract."""

import json
from pathlib import Path

from app.services.grid_aggregator import aggregate_matches


def test_aggregator_computes_focus_side_metrics_and_map_coordinates() -> None:
    project_root = Path(__file__).resolve().parents[2]
    payload = json.loads((project_root / "data" / "sample_grid_match.json").read_text(encoding="utf-8"))

    metrics = aggregate_matches(payload["matches"])

    assert metrics["matches"] == 2
    assert metrics["gd_at_15"] == 530.0
    assert metrics["fb_rate"] == 100.0
    assert metrics["ft_rate"] == 50.0
    assert metrics["objective_capture_rates"]["first_dragon_capture_rate"] == 50.0
    assert metrics["objective_capture_rates"]["first_voidgrubs_capture_rate"] == 50.0
    assert len(metrics["jungle_pathing_0_5"]) == 12
    assert len(metrics["pre_objective_ward_coordinates"]) == 4


def test_aggregator_returns_full_empty_metric_shape() -> None:
    metrics = aggregate_matches([])

    assert metrics["matches"] == 0
    assert metrics["jungle_pathing_0_5"] == []
    assert metrics["pre_objective_ward_coordinates"] == []
    assert set(metrics["objective_capture_rates"]) == {
        "first_dragon_capture_rate",
        "first_voidgrubs_capture_rate",
        "first_rift_herald_capture_rate",
        "first_baron_capture_rate",
    }