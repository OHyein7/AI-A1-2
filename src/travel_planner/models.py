"""Data objects shared by API clients, planner, and file writers."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class Recommendation:
    recommended_city: str
    weather: str
    events: list[str]
    reason: str

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Recommendation":
        required = ("recommended_city", "weather", "events", "reason")
        if not all(key in data for key in required) or not isinstance(data["events"], list):
            raise ValueError("LLM JSON에 필수 키(recommended_city, weather, events, reason)가 없습니다.")
        return cls(
            recommended_city=str(data["recommended_city"]),
            weather=str(data["weather"]),
            events=[str(event) for event in data["events"]],
            reason=str(data["reason"]),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Place:
    name: str
    address: str
    category: str = ""
    url: str = ""
    x: str = ""
    y: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PipelineError:
    step: str
    type: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

