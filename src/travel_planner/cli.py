"""Argument parsing and user-facing execution log."""

from __future__ import annotations

import argparse
from datetime import date

from travel_planner.clients import KakaoLocalClient, OpenAIClient
from travel_planner.config import Settings
from travel_planner.planner import TravelPlanner
from travel_planner.storage import save_results


def parse_date(value: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as error:
        raise argparse.ArgumentTypeError("날짜는 YYYY-MM-DD 형식이어야 합니다.") from error


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="LLM과 Kakao Local API를 활용한 국내 여행 추천기")
    parser.add_argument("--date", required=True, type=parse_date, help="여행 날짜 (YYYY-MM-DD)")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings.from_environment()
    try:
        settings.require_openai_key()
    except ValueError as error:
        raise SystemExit(f"오류: {error}") from error

    planner = TravelPlanner(OpenAIClient(settings.openai_api_key, settings.openai_model), KakaoLocalClient(settings.kakao_rest_api_key))
    print("[1/3] 1차 추천 생성 중(LLM)...")
    recommendation, places, report, errors = planner.run(args.date)
    print(f"- recommended_city: {recommendation.recommended_city}")
    print("[2/3] 맛집 검색 완료" if places else "[2/3] 맛집 데이터 없음 — 리포트 생성을 계속합니다.")
    raw_path, report_path = save_results(args.date, recommendation, places, report, errors)
    print("[3/3] 최종 리포트 생성 완료")
    print(f"완료! {raw_path} 및 {report_path}를 확인하세요.")

