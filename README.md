# 🗺️ Korea Travel Planner

> 여행 날짜 하나로 **LLM 추천 → 국내 맛집 검색 → Markdown 여행 리포트**를 완성하는 Python CLI 파이프라인

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/LLM-OpenAI_Responses_API-412991?logo=openai&logoColor=white)
![Kakao](https://img.shields.io/badge/Places-Kakao_Local-FFCD00?logo=kakao&logoColor=111111)

## ✨ 무엇을 하나요?

`Korea Travel Planner`는 날짜를 입력받아 AI가 여행하기 좋은 국내 도시와 계절 정보를 구조화된 JSON으로 추천하고, Kakao Local API로 맛집을 찾은 뒤, 최종 여행 리포트를 Markdown으로 저장합니다.

```text
--date  →  OpenAI 추천 JSON  →  Kakao 맛집 검색  →  Markdown 리포트
```

Codyssey **A1-2 — Python 응용: API 활용 국내 여행지 추천 프로그램 개발** 미션 결과물입니다.

## 🧭 핵심 기능

| 단계 | 입력 | 처리 | 출력 |
| --- | --- | --- | --- |
| 1. 도시 추천 | 여행 날짜 | LLM에 JSON 형식 응답 요청 | 도시·날씨·행사·추천 이유 |
| 2. 맛집 검색 | 추천 도시 | Kakao Local 키워드 검색 | 최대 5개 장소 정보 |
| 3. 리포트 생성 | 추천 JSON + 장소 목록 | LLM Markdown 리포트 생성 | 1일 일정 포함 여행 안내 |
| 4. 결과 저장 | 전체 실행 결과 | JSON/Markdown 파일 기록 | `results/` 폴더 |

## 🚀 빠른 시작

### 1. 준비물

- Python 3.10 이상
- OpenAI API 키
- Kakao Developers REST API 키

```bash
git clone https://github.com/OHyein7/AI-A1-2.git
cd AI-A1-2
```

### 2. API 키 설정

`.env.example`을 복사해 `.env`를 만들고 **본인의 키만** 입력합니다.

```powershell
Copy-Item .env.example .env
```

```dotenv
OPENAI_API_KEY=your_openai_key_here
KAKAO_REST_API_KEY=your_kakao_rest_api_key_here
OPENAI_MODEL=gpt-4.1-mini
```

> `.env`는 `.gitignore`에 포함되어 GitHub에 올라가지 않습니다. 키를 코드, README, 커밋 메시지, 실행 결과 파일에 절대 붙여 넣지 마세요. 키를 환경변수로 분리하면 공유 중 유출을 막고, 키 교체 시 코드를 바꿀 필요가 없습니다.

Windows PowerShell에서 한 번만 환경변수로 주입할 수도 있습니다.

```powershell
$env:OPENAI_API_KEY="YOUR_KEY"
$env:KAKAO_REST_API_KEY="YOUR_KEY"
```

### 3. 실행

외부 Python 패키지 없이 표준 라이브러리로 실행됩니다.

```bash
python travel_planner.py --date "2026-10-01"
```

날짜 형식이 올바르지 않으면 `argparse`가 사용법을 출력하고 종료합니다.

```text
error: argument --date: 날짜는 YYYY-MM-DD 형식이어야 합니다.
```

## 📁 결과물

실행할 때마다 `results/`에 다음 파일을 생성합니다.

```text
results/
├── 2026-10-01_raw.json          # 1차 추천 + 맛집 목록 + 오류 배열
└── 2026-10-01_travel_plan.md    # 최종 여행 리포트
```

`raw.json`은 최소한 아래 구조를 갖습니다.

```json
{
  "recommendation": {
    "recommended_city": "제주",
    "weather": "3월 중순에는 온화합니다.",
    "events": ["봄 지역 행사"],
    "reason": "추천 근거"
  },
  "restaurants": [],
  "errors": []
}
```

최종 리포트에는 추천 지역·이유, 날씨, 행사, 맛집, 오전/오후/저녁 일정, 오류 요약이 포함됩니다. 맛집이 없거나 장소 API가 실패해도 리포트 생성을 멈추지 않고 **데이터 없음**으로 표시합니다.

## 🛡️ 오류 처리 전략

| 상황 | 동작 |
| --- | --- |
| `OPENAI_API_KEY` 없음 | 즉시 종료하고 `.env` 설정 방법 안내 |
| LLM JSON 파싱 실패 | 한 번만 재요청한 뒤 실패 시 종료 |
| Kakao 인증/쿼터/네트워크 실패 | 맛집을 빈 목록으로 처리하고 리포트 생성 계속 |
| 맛집 검색 0건 | 오류 없이 `데이터 없음`으로 리포트 생성 |
| 최종 리포트 LLM 실패 | 추천 JSON을 바탕으로 기본 Markdown 리포트 생성 |

## 🧠 API와 데이터 흐름

- **REST API**는 HTTP 요청으로 데이터를 주고받는 방식입니다. 이 프로젝트는 OpenAI에 `POST`로 생성 요청을 보내고, Kakao에 `GET`으로 장소를 검색합니다.
- LLM의 1차 출력을 JSON으로 강제해 `recommended_city`를 다음 Kakao 검색의 입력으로 안전하게 연결합니다.
- 네트워크·인증·쿼터·JSON 파싱 오류는 `try-except`로 분리해, 가능한 단계까지 결과를 저장합니다.

## 🗂️ 프로젝트 구조

```text
AI-A1-2/
├── travel_planner.py             # 실행 진입점
├── src/travel_planner/
│   ├── cli.py                    # argparse와 진행 로그
│   ├── config.py                 # .env / 환경변수 로드
│   ├── clients.py                # OpenAI·Kakao HTTP 클라이언트
│   ├── models.py                 # 추천·장소·오류 데이터 모델
│   ├── planner.py                # 파이프라인과 오류 복구
│   └── storage.py                # JSON·Markdown 결과 저장
└── tests/                        # 네트워크 없는 단위 테스트
```

## ✅ 테스트

```bash
python -c "import sys,unittest; sys.path.insert(0,'src'); unittest.main(module=None, argv=['','discover','-s','tests'])"
```

테스트는 장소 검색 API가 `401` 오류를 내도 리포트 생성이 계속되는지를 검증합니다.

## 🔮 확장 아이디어

- 추천 도시를 2~3개로 확장하고 지역별 장소 검색 반복
- 동일한 날짜의 원본 JSON을 캐시해 API 호출 비용 절감
- Naver Local API 어댑터 추가

---

OpenAI Responses API는 텍스트 입력과 JSON 출력을 지원하며, 이 프로젝트는 그 흐름을 1차 추천·최종 리포트 단계에 사용합니다. [공식 API 참고](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)
