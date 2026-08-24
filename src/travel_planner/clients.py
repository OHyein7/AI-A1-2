"""Minimal HTTP clients for OpenAI Responses and Kakao Local APIs."""

from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from travel_planner.models import Place, Recommendation


class ApiError(RuntimeError):
    """An API request, authentication, quota, or parsing failure."""


def request_json(url: str, *, method: str = "GET", headers: dict[str, str] | None = None, body: object | None = None) -> dict[str, Any]:
    payload = json.dumps(body).encode("utf-8") if body is not None else None
    request = Request(url, data=payload, method=method, headers=headers or {})
    try:
        with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed HTTPS endpoints
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise ApiError(f"HTTP {error.code}") from error
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        raise ApiError(str(error)) from error


class OpenAIClient:
    endpoint = "https://api.openai.com/v1/responses"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def _ask_json(self, instructions: str, prompt: str) -> dict[str, Any]:
        data = request_json(
            self.endpoint,
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            body={
                "model": self.model,
                "instructions": instructions,
                "input": prompt,
                "store": False,
                "text": {"format": {"type": "json_object"}},
            },
        )
        if isinstance(data.get("output_text"), str):
            return json.loads(data["output_text"])
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    return json.loads(content["text"])
        raise ApiError("OpenAI 응답에서 JSON 텍스트를 찾지 못했습니다.")

    def recommend(self, travel_date: str) -> Recommendation:
        data = self._ask_json(
            "You are a Korean domestic travel planner. Reply with JSON only.",
            f"Recommend one Korean city for {travel_date}. JSON keys: recommended_city (string), weather (string), events (array of 1-3 strings), reason (2-4 Korean sentences). General seasonal information is acceptable.",
        )
        return Recommendation.from_dict(data)

    def write_report(self, travel_date: str, recommendation: Recommendation, places: list[Place], errors: list[str]) -> str:
        restaurants = [place.to_dict() for place in places]
        data = self._ask_json(
            "You are a Korean travel editor. Reply with JSON only.",
            "Create a Korean Markdown travel report. Return JSON with one key 'markdown'. Include headings for recommended city, reason, weather, events, restaurants (say 데이터 없음 if empty), a one-day morning/afternoon/evening itinerary, and errors. "
            + json.dumps({"date": travel_date, "recommendation": recommendation.to_dict(), "restaurants": restaurants, "errors": errors}, ensure_ascii=False),
        )
        markdown = data.get("markdown")
        if not isinstance(markdown, str) or not markdown.strip():
            raise ApiError("최종 리포트 JSON에 markdown 문자열이 없습니다.")
        return markdown


class KakaoLocalClient:
    endpoint = "https://dapi.kakao.com/v2/local/search/keyword.json"

    def __init__(self, rest_api_key: str) -> None:
        self.rest_api_key = rest_api_key

    def search_restaurants(self, city: str, size: int = 5) -> list[Place]:
        query = urlencode({"query": f"{city} 맛집", "size": size})
        data = request_json(
            f"{self.endpoint}?{query}",
            headers={"Authorization": f"KakaoAK {self.rest_api_key}"},
        )
        return [
            Place(
                name=str(item.get("place_name", "")),
                address=str(item.get("road_address_name") or item.get("address_name", "")),
                category=str(item.get("category_name", "")),
                url=str(item.get("place_url", "")),
                x=str(item.get("x", "")),
                y=str(item.get("y", "")),
            )
            for item in data.get("documents", [])
        ]

