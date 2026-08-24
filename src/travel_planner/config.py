"""Safe environment configuration without adding third-party dependencies."""

from __future__ import annotations

from dataclasses import dataclass
from os import environ
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Load simple KEY=VALUE pairs without overriding already-exported variables."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", maxsplit=1)
        environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True, slots=True)
class Settings:
    openai_api_key: str
    kakao_rest_api_key: str
    openai_model: str

    @classmethod
    def from_environment(cls) -> "Settings":
        load_dotenv()
        return cls(
            openai_api_key=environ.get("OPENAI_API_KEY", "").strip(),
            kakao_rest_api_key=environ.get("KAKAO_REST_API_KEY", "").strip(),
            openai_model=environ.get("OPENAI_MODEL", "gpt-4.1-mini").strip(),
        )

    def require_openai_key(self) -> None:
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 없습니다. .env.example을 .env로 복사해 키를 설정하세요.")

