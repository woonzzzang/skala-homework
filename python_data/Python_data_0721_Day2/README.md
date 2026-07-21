# Python Data Day2 실습 실행 안내

작성자: 4기 광주 3반 정다운  
제출 폴더: `Python_data_0721_Day2`

## 1. 실행 전 확인

이 폴더는 `uv` 환경에서도 실행할 수 있도록 `requirements.txt`를 포함합니다.

가상환경 폴더인 `.venv`는 제출하지 않습니다. 실행하는 사람이 아래 명령으로 새로 만들면 됩니다.

## 2. 데이터 폴더 위치

현재 코드들은 수업 폴더 구조 기준으로 `../data` 폴더의 데이터를 읽습니다.

권장 구조:

```text
python_data/
├── data/
│   ├── sales_raw.csv
│   ├── events_large.csv
│   ├── telco_churn.csv
│   └── ...
└── Python_data_0721_Day2/
    ├── requirements.txt
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

`Python_data_0721_Day2` 폴더만 따로 압축 해제한 경우에도, `data` 폴더는 `Python_data_0721_Day2`와 같은 상위 폴더 아래에 있어야 합니다.

예시:

```text
제출확인폴더/
├── data/
└── Python_data_0721_Day2/
```

## 3. 의존성 설치 방법

### 방법 1. uv 1회 실행 방식

가상환경을 직접 활성화하지 않고 실행할 수 있는 방식입니다.

```bash
cd Python_data_0721_Day2
uv run --with-requirements requirements.txt python 'practice 4/solution.py'
```

다른 파일도 같은 방식으로 실행하면 됩니다.

### 방법 2. uv 가상환경 생성 후 실행

여러 파일을 한 번에 확인할 때 권장합니다.

```bash
cd Python_data_0721_Day2
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate
```

이후에는 `python` 명령으로 실행합니다.

```bash
python 'practice 4/solution.py'
python 'practice 5/solution.py'
python 'Total 2/analysis.py'
python 'Total 3/report.py'
python 'Advanced/analysis.py'
```

## 4. 주요 실행 명령

### Practice 1

```bash
python 'practice 1/solution.py'
```

### Practice 2

```bash
python 'practice 2/solution.py'
```

### Practice 3

```bash
python 'practice 3/solution.py'
```

### Practice 4

```bash
python 'practice 4/solution.py'
```

Pandas 데이터 정제, 결측치 처리, IQR 윈저라이징, groupby/pivot/merge 수행

### Practice 5

```bash
python 'practice 5/solution.py'
```

Pandas, Polars Lazy, DuckDB 동일 집계 결과 검증 및 실행 시간 비교

### Total 1

```bash
python 'Total 1/pipeline.py'
pytest -v 'Total 1'
```

비동기 ETL, Pydantic 검증, CSV/Parquet 저장, 단위 테스트 수행

### Total 2

```bash
python 'Total 2/analysis.py'
```

EDA, Plotly 시각화, 통계 검정, ML Pipeline 학습 및 모델 저장

### Total 3

```bash
python 'Total 3/report.py'
```

HTML 리포트 1회 생성

스케줄러 기본 1회 실행:

```bash
python 'Total 3/run_scheduler.py'
```

반복 실행 예시:

```bash
python 'Total 3/run_scheduler.py' --interval 10 --mode schedule
```

### Advanced

```bash
python 'Advanced/analysis.py'
```

여러 CSV 파일을 대상으로 데이터 품질 감사 리포트 생성

## 5. 코드 품질 확인

Ruff 검사:

```bash
ruff check 'practice 4' 'practice 5' 'Total 2' 'Total 3' 'Advanced'
```

문법 컴파일 확인:

```bash
python -m py_compile \
  'practice 4/solution.py' \
  'practice 5/solution.py' \
  'Total 2/analysis.py' \
  'Total 3/config.py' \
  'Total 3/report.py' \
  'Total 3/run_scheduler.py' \
  'Advanced/analysis.py'
```

## 6. 제출 시 포함 여부

포함 권장:

- 각 실습 폴더
- 각 실습의 `readme.md`
- `requirements.txt`
- 실행 결과가 필요한 `output/`, `assets/`

제외 권장:

- `.venv`
- `__pycache__`
- `.ruff_cache`

## 7. 참고

각 실습별 자세한 수행 내용은 폴더 내부 `readme.md`에 정리했습니다.

채점 환경에서 `uv`가 없다면 일반 `venv`로도 실행할 수 있습니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
