import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator
from typing_extensions import Annotated


BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR.parent.parent / "data" / "api_response.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(message)s")
logger = logging.getLogger(__name__)


class Profile(BaseModel):
    country: Annotated[str, Field(min_length=2)]
    tier: str
    score: Annotated[float, Field(ge=0, le=100)]

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        value = value.strip().upper()
        if not value:
            raise ValueError("country는 비어 있을 수 없습니다.")
        return value

    @field_validator("tier")
    @classmethod
    def normalize_tier(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in {"free", "pro", "enterprise"}:
            raise ValueError("tier는 free/pro/enterprise 중 하나여야 합니다.")
        return value


class User(BaseModel):
    id: Annotated[int, Field(gt=0)]
    username: Annotated[str, Field(min_length=1)]
    email: str
    age: Annotated[int, Field(ge=0, le=120)]
    is_active: bool
    signup_date: Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")]
    profile: Profile
    tags: List[str] = []

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip()
        if "@" not in value or "." not in value.split("@")[-1]:
            raise ValueError("email 형식이 올바르지 않습니다.")
        return value

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, values: List[str]) -> List[str]:
        return [value.strip().lower() for value in values]


class ApiResponse(BaseModel):
    status: str
    count: Annotated[int, Field(ge=0)]
    results: List[Dict[str, object]]

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        value = value.strip().lower()
        if value != "ok":
            raise ValueError("status는 ok여야 합니다.")
        return value


def load_json(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def log_sample(users: List[Dict[str, object]]) -> None:
    logger.info("전체 건수: %s", len(users))
    logger.info("-- 정상 샘플 1건 --")
    logger.info("\n%s", json.dumps(users[0], indent=2, ensure_ascii=False))

    logger.info("-- 앞 10건 key/type 확인 --")
    for i, row in enumerate(users[:10]):
        logger.info("%s %s", i, {key: type(value).__name__ for key, value in row.items()})


def serialize_errors(error: ValidationError) -> List[Dict[str, object]]:
    serialized = []

    for item in error.errors():
        clean_item = item.copy()
        if "ctx" in clean_item:
            clean_item["ctx"] = {
                key: str(value)
                for key, value in clean_item["ctx"].items()
            }
        serialized.append(clean_item)

    return serialized


def validate_users(users: List[Dict[str, object]]) -> tuple[List[User], List[Dict[str, object]]]:
    valid = []
    invalid = []

    for index, row in enumerate(users):
        try:
            valid.append(User.model_validate(row))
        except ValidationError as error:
            invalid.append(
                {
                    "index": index,
                    "data": row,
                    "errors": serialize_errors(error),
                }
            )

    return valid, invalid


def log_error_table(invalid: List[Dict[str, object]]) -> None:
    logger.info("-- 오염 데이터 실패 사유 --")
    logger.info("%-4s%-20s%s", "행", "필드", "사유")
    for item in invalid:
        for error in item["errors"]:
            field = ".".join(str(value) for value in error["loc"])
            logger.info("%-4s%-20s%s", item["index"], field, error["msg"])


def main() -> int:
    data = load_json(DATA_PATH)
    users = data["results"]

    log_sample(users)

    valid, invalid = validate_users(users)

    logger.info("-- 검증 결과 --")
    logger.info("전체 %s건 -> 유효 %s / 오염 %s", len(users), len(valid), len(invalid))
    log_error_table(invalid)

    response = ApiResponse.model_validate(data)
    assert response.count == len(users)
    assert len(valid) == 36
    assert len(invalid) == 4

    logger.info("-- 성공 판정 기준 통과 --")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
