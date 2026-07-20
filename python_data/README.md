# Python Data Analysis Practice

SKALA 데이터 분석 Python 실습 정리 저장소입니다.

Day1에서는 Python 기본 자료구조, 제너레이터, Pydantic 검증, asyncio 비동기 처리, ETL 파이프라인 구성을 실습했습니다.

Day2는 아직 진행 전이므로 폴더와 정리 구조만 준비해두었습니다.

## 1. 폴더 구조

```text
python_data/
├── data/
├── Python_data_0720_Day1/
│   ├── ex01_streaming_agg/
│   ├── ex02_pydantic_validation/
│   ├── ex03_async_collector/
│   └── capstone01_async_etl/
└── Python_data_0721_Day2/
    ├── ex04_pandas_cleaning/
    ├── ex05_polars_duckdb/
    ├── capstone02_eda_ml/
    ├── capstone03_automation/
    └── Advanced/
```

## 2. 실행 환경

`uv` 기반 Python 프로젝트로 관리했습니다.

주요 사용 패키지:

- `pydantic`
- `pandas`
- `pyarrow`
- `pytest`
- `ruff`

기본 실행 예시:

```bash
uv run python Python_data_0720_Day1/ex01_streaming_agg/solution.py
uv run pytest -v Python_data_0720_Day1/capstone01_async_etl
uv run ruff check .
```

## 3. Day1 실습 내용

### ex01_streaming_agg

대용량 로그 파일 `web_logs.csv` 20만 건을 한 번에 메모리에 올리지 않고 제너레이터로 한 줄씩 읽어 집계하는 실습입니다.

주요 내용:

- `yield` 기반 제너레이터 파일 읽기
- `Counter`를 사용한 상태코드, 경로, IP, 시간대별 요청 수 집계
- `defaultdict(Counter)`를 사용한 시간대별 상태코드 요청 수 집계
- `functools.reduce()`를 사용한 fold 패턴 적용
- `tracemalloc`으로 `readlines()` 방식과 제너레이터 방식의 메모리 사용량 비교

결과:

- 총 요청 수 200,000건 확인
- 5xx 오류율 약 8% 확인
- 경로별, 시간대별, IP별 요약 리포트 출력

상세 내용: [ex01 readme](./Python_data_0720_Day1/ex01_streaming_agg/readme.md)

### ex02_pydantic_validation

API 응답 JSON 데이터 40건을 Pydantic v2 모델로 검증하고, 유효 데이터와 오염 데이터를 분리하는 실습입니다.

주요 내용:

- `BaseModel`, `Field`, `Annotated` 기반 스키마 정의
- `field_validator`를 사용한 커스텀 검증
- 중첩 모델을 사용한 `profile.score` 검증
- `ValidationError` 기반 오류 사유 수집
- 유효/무효 레코드 건수와 실패 사유 표 출력

결과:

- 전체 40건 중 유효 36건, 오염 4건 분리
- 실패 필드와 실패 사유 출력
- `main()` 구조 적용

상세 내용: [ex02 readme](./Python_data_0720_Day1/ex02_pydantic_validation/readme.md)

### ex03_async_collector

`asyncio` 기반 비동기 수집기를 만들고, 여러 요청을 동시에 처리하는 실습입니다.

주요 내용:

- `async def`, `await`, `asyncio.gather()` 사용
- `Semaphore`로 동시 요청 수 제한
- `asyncio.wait_for()` 기반 요청별 타임아웃 적용
- 지수 백오프 재시도
- 최종 실패 데이터 `dead_letter.json` 격리

결과:

- mock 요청 60건 처리
- 약 1.7초 내외 비동기 처리 확인
- 동기 방식 대비 대기시간 감소 확인

상세 내용: [ex03 readme](./Python_data_0720_Day1/ex03_async_collector/readme.md)

### capstone01_async_etl

ex02의 Pydantic 검증과 ex03의 비동기 수집을 합쳐 재사용 가능한 ETL 파이프라인을 구성한 종합실습입니다.

주요 내용:

- Extract: 비동기 mock 데이터 수집
- Transform: Pydantic 검증으로 유효/무효 데이터 분리
- Load: 유효 데이터를 CSV와 Parquet로 저장
- Orchestrate: `run()` 함수로 전체 단계 조율
- pytest 테스트 6개 작성
- ruff 코드 품질 검사 및 포맷 적용

결과:

- 전체 60건 수집
- 유효 56건, 무효 4건 분리
- `products.csv`, `products.parquet`, `invalid_records.json` 생성
- pytest 6개 통과
- ruff check 통과

상세 내용: [capstone01 readme](./Python_data_0720_Day1/capstone01_async_etl/readme.md)

## 4. Day2 실습 내용

Day2는 아직 진행 전입니다.

### ex04_pandas_cleaning

예정 내용:

- 

상세 내용:

- 

### ex05_polars_duckdb

예정 내용:

- 

상세 내용:

- 

### capstone02_eda_ml

예정 내용:

- 

상세 내용:

- 

### capstone03_automation

예정 내용:

- 

상세 내용:

- 

### Advanced

예정 내용:

- 

상세 내용:

- 
