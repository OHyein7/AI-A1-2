"""Pipeline orchestration: recommendation -> place search -> Markdown report."""

from __future__ import annotations

from travel_planner.clients import ApiError
from travel_planner.models import PipelineError, Place, Recommendation


class TravelPlanner:
    def __init__(self, llm: object, places: object) -> None:
        self.llm = llm
        self.places = places

    def run(self, travel_date: str) -> tuple[Recommendation, list[Place], str, list[PipelineError]]:
        errors: list[PipelineError] = []
        try:
            recommendation = self.llm.recommend(travel_date)
        except (ApiError, ValueError) as first_error:
            try:
                recommendation = self.llm.recommend(travel_date)
            except (ApiError, ValueError) as second_error:
                raise RuntimeError(f"LLM 추천 JSON 생성 실패(재시도 후): {second_error}") from first_error

        try:
            restaurants = self.places.search_restaurants(recommendation.recommended_city)
        except ApiError as error:
            restaurants = []
            errors.append(PipelineError("place_search", "API_ERROR", str(error)))

        try:
            report = self.llm.write_report(travel_date, recommendation, restaurants, [error.message for error in errors])
        except ApiError as error:
            errors.append(PipelineError("report_generation", "API_ERROR", str(error)))
            report = self._fallback_report(travel_date, recommendation, restaurants, errors)
        return recommendation, restaurants, report, errors

    @staticmethod
    def _fallback_report(travel_date: str, recommendation: Recommendation, places: list[Place], errors: list[PipelineError]) -> str:
        restaurant_lines = "\n".join(f"- {place.name}: {place.address}" for place in places) or "- 데이터 없음"
        event_lines = "\n".join(f"- {event}" for event in recommendation.events) or "- 데이터 없음"
        error_lines = "\n".join(f"- [{error.step}] {error.message}" for error in errors) or "- 없음"
        return f"# {travel_date} 국내 여행 추천 리포트\n\n## 추천 지역\n{recommendation.recommended_city}\n\n## 추천 이유\n{recommendation.reason}\n\n## 날씨 요약\n{recommendation.weather}\n\n## 행사/축제\n{event_lines}\n\n## 맛집 추천\n{restaurant_lines}\n\n## 1일 일정 제안\n- 오전: 지역 산책\n- 오후: 대표 명소 방문\n- 저녁: 맛집 탐방\n\n## 오류 요약(errors)\n{error_lines}\n"

