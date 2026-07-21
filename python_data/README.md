# Python Data Analysis Practice

SKALA 데이터 분석 Python 실습 정리 저장소입니다.

Day1에서는 Python 기본 자료구조, 제너레이터, Pydantic 검증, asyncio 비동기 처리, ETL 파이프라인 구성을 실습했습니다.

Day2에서는 Pandas 데이터 정제, Polars/DuckDB 성능 비교, EDA·통계·ML 파이프라인, 분석 자동화 리포트 생성, Advanced 자율 실습을 수행했습니다.

Day1과 Day2에 유사한 이름의 실습 폴더가 함께 존재하는 이유는 교수님 제출 요청에 맞춰 날짜별 실습 폴더를 따로 구성했기 때문입니다.

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
    ├── practice 1/
    ├── practice 2/
    ├── practice 3/
    ├── practice 4/
    ├── practice 5/
    ├── Total 1/
    ├── Total 2/
    ├── Total 3/
    └── Advanced/
```

## 2. 실행 환경

`uv` 기반 Python 프로젝트로 관리했습니다.

주요 사용 패키지:

- `pydantic`
- `pandas`
- `pyarrow`
- `polars`
- `duckdb`
- `plotly`
- `seaborn`
- `scipy`
- `scikit-learn`
- `joblib`
- `jinja2`
- `schedule`
- `pytest`
- `ruff`

기본 실행 예시:

```bash
uv run python Python_data_0720_Day1/ex01_streaming_agg/solution.py
uv run pytest -v Python_data_0720_Day1/capstone01_async_etl
uv run ruff check .
```

`Python_data_0721_Day2` 폴더만 따로 제출하거나 확인하는 경우에는 해당 폴더 내부의 [Day2 실행 안내](./Python_data_0721_Day2/README.md)를 참고하면 됩니다.

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

Day2 폴더는 교수님 요청에 맞춰 `practice 1~5`, `Total 1~3`, `Advanced` 구조로 정리했습니다.

`practice 1~3`, `Total 1`은 Day1에서 배운 개념을 Day2 제출 구조에 맞춰 다시 배치한 실습이며, `practice 4`, `practice 5`, `Total 2`, `Total 3`, `Advanced`는 Day2 내용에 맞춰 추가 수행한 실습입니다.

### practice 1

대용량 로그 스트리밍 집계 실습입니다.

주요 내용:

- 제너레이터 기반 파일 읽기
- `Counter`, `defaultdict` 기반 누적 집계
- 시간대별, 상태코드별, IP별 리포트 출력
- `tracemalloc` 메모리 비교

상세 내용: [practice 1 readme](./Python_data_0721_Day2/practice%201/readme.md)

### practice 2

Pydantic v2 데이터 검증 실습입니다.

주요 내용:

- 타입 힌트와 `BaseModel` 기반 스키마 정의
- `ValidationError`로 유효/무효 데이터 분리
- 실패 필드와 실패 사유 표 출력

상세 내용: [practice 2 readme](./Python_data_0721_Day2/practice%202/readme.md)

### practice 3

`asyncio` 기반 비동기 수집기 실습입니다.

주요 내용:

- `async/await`, `gather`, `Semaphore` 적용
- 요청별 타임아웃과 재시도 처리
- 실패 데이터 `dead_letter.json` 격리

상세 내용: [practice 3 readme](./Python_data_0721_Day2/practice%203/readme.md)

### practice 4

Pandas 2.x 데이터 정제 실습입니다.

주요 내용:

- `sales_raw.csv` 데이터 진단
- 결측치 처리와 타입 정규화
- IQR 기준 이상치 후보 윈저라이징
- `groupby.agg`, `pivot_table`, `merge` 수행
- 정제 결과 `sales_clean.csv` 저장

상세 내용: [practice 4 readme](./Python_data_0721_Day2/practice%204/readme.md)

### practice 5

Polars와 DuckDB 성능 비교 실습입니다.

주요 내용:

- Pandas, Polars Lazy, DuckDB로 같은 질의 작성
- `scan_csv → filter → group_by → agg → sort → collect` 체인 구현
- 세 엔진 결과 일치 검증
- `timeit`으로 동일 반복 횟수 기준 실행 시간 비교

상세 내용: [practice 5 readme](./Python_data_0721_Day2/practice%205/readme.md)

### Total 1

비동기 ETL 파이프라인 종합 실습입니다.

주요 내용:

- 비동기 수집
- Pydantic 검증
- CSV/Parquet 저장
- pytest 단위 테스트
- ruff 코드 품질 확인

상세 내용: [Total 1 readme](./Python_data_0721_Day2/Total%201/readme.md)

### Total 2

EDA, 통계 분석, ML Pipeline 종합 실습입니다.

주요 내용:

- Polars EDA
- Plotly 인터랙티브 시각화
- t-test, chi-square 검정과 p-value 해석
- `ColumnTransformer`와 `Pipeline` 기반 전처리·모델 학습
- 정확도, F1-score, ROC-AUC 출력
- `joblib` 모델 저장과 재로딩 확인

결과:

- ROC-AUC 0.6727
- Accuracy 0.6400
- F1-score 0.4412
- HTML 시각화 3종과 모델 파일 생성

상세 내용: [Total 2 readme](./Python_data_0721_Day2/Total%202/readme.md)

### Total 3

분석 자동화와 HTML 리포트 생성 실습입니다.

주요 내용:

- `config.py` frozen dataclass 설정 분리
- Jinja2 템플릿 기반 HTML 리포트 생성
- KPI, 카테고리별 매출, 지역별 매출, 월별 매출 집계
- Plotly 차트 삽입
- `run_scheduler.py`로 1회 실행과 반복 실행 지원

상세 내용: [Total 3 readme](./Python_data_0721_Day2/Total%203/readme.md)

### Advanced

Day2 자율 심화 실습입니다.

주요 내용:

- `data` 폴더의 여러 CSV 파일을 대상으로 데이터 품질 감사
- 결측률, 중복률, IQR 이상치 후보율, 품질 점수 계산
- Seaborn 정적 차트와 Plotly 인터랙티브 차트 생성
- Markdown 자동 리포트 생성

상세 내용: [Advanced readme](./Python_data_0721_Day2/Advanced/readme.md)
