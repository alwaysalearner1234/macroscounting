"""Grounded coaching prompt construction from verified scouting metrics."""

import json
from typing import Any


def build_grounded_prompt(question: str, verified_metrics: dict[str, Any]) -> str:
    """Build a prompt that treats aggregator JSON as the only factual source.

    This function prepares a prompt but does not call an LLM. Metric values are
    serialized directly from the trusted aggregator/report boundary.
    """
    metrics = json.dumps(verified_metrics, sort_keys=True, ensure_ascii=True, allow_nan=False)
    return (
        "You are a League of Legends macro coach. Answer the coach's question using only the "
        "verified metrics JSON below. Do not infer sample sizes, causes, or statistics that are "
        "not present. If evidence is insufficient, say so explicitly. Cite the relevant metric "
        "names and values.\n\n"
        f"Verified scouting metrics JSON:\n{metrics}\n\n"
        f"Coach question:\n{question.strip()}"
    )