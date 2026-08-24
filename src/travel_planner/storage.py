"""Write JSON source data and Markdown reports to results/ safely."""

from __future__ import annotations

import json
from pathlib import Path

from travel_planner.models import PipelineError, Place, Recommendation


def save_results(travel_date: str, recommendation: Recommendation, places: list[Place], report: str, errors: list[PipelineError]) -> tuple[Path, Path]:
    results = Path("results")
    results.mkdir(exist_ok=True)
    raw_path = results / f"{travel_date}_raw.json"
    report_path = results / f"{travel_date}_travel_plan.md"
    raw_path.write_text(
        json.dumps(
            {"recommendation": recommendation.to_dict(), "restaurants": [place.to_dict() for place in places], "errors": [error.to_dict() for error in errors]},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    report_path.write_text(report, encoding="utf-8")
    return raw_path, report_path

