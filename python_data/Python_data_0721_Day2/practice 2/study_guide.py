import json

# STEP 0 : 오염된 4건이 '어떻게' 오염됐는지 먼저 찾아보기

data = json.load(open('../../data/api_response.json', encoding='utf-8'))
users = data['results']

print('전체 건수:', len(users)) # 40
print(json.dumps(users[0], indent=2, ensure_ascii=False)) # 정상 샘플 1건

# 어떤 키들이 있는지, 값 타입이 뭔지 훑어보기
# 힌트: 음수 가격/타입 이상/필수 필드 누락/범위 초과를 의심하세요.
# for i, row in enumerate(users[:10]):
#     print(i, {k: type(v).__name__ for k, v in row.items()})

# STEP 1 : 가장 단순한 모델 하나 만들기 (필드 2개만)

# from pydantic import BaseModel

# class Product(BaseModel):
#     id: int     # 이 이름의 필드가 있어야 하고, 정수여야 함
#     name: str   # 문자열이어야 함

# # 테스트 : 정상 데이터
# p = Product(id=1, name='사과')
# print(p)

# # 테스트 : 잘못된 데이터 -> ValidationError 발생
# try: 
#     Product(id='숫자아님', name='사과')
# except Exception as e:
#     print('걸림!', e)

# STEP 2 : 범위, 제약 조건 초가 - Field()
# "양수여야 한다"는 비즈니스 규칙은 'Field()'로 표현

# from pydantic import BaseModel, Field
# from typing import Annotated

# class Product(BaseModel):
#     id: int
#     name: str
#     price: float = Field(gt=0) # gt = greater than 0 = 양수
#     quantity: int = Field(ge=0, le=10000) # 0 이상 10000 이하 

# gt(초과) ge(이상) lt(미만) le(이하)

# STEP 3 : 커스텀 규칙 - field_validator
# 'Field()'로 표현 안 되는 규칙은 직접 함수로 구현

from pydantic import BaseModel, Field, field_validator

class Product(BaseModel):
    name: str
    category: str

    @field_validator('category')
    @classmethod
    def normalize_category(cls, v: str) -> str:
        v = v.strip().lower()     # 앞뒤 공백 제거 + 소문자화
        if not v:
            raise ValueError('category는 비어 있을 수 없습니다.')
        return v  # 반드시 값을 return
    
# 검증기는 '검사' 뿐 아니라 '정규화'도 수행
# Food -> food로 다듬어서 돌려주면, 뒷단 코드는 항상 깨끗한 값만 봄 

# STEP 4 : 중첩 구조 - 모델 안에 모델
# JSON이 `{"Product": {...}, "Seller":{...}}` 처럼 상자 안에 상자라면, 모델도 모델 안에 모델로 만듦

from typing import List

class Seller(BaseModel):    # 안쪽 상자
    seller_id: int
    region: str

class Product(BaseModel):   # 바깥 상자
    id: int
    price: float = Field(gt=0)
    seller: Seller          # 타입 자리에 다른 모델을 넣음
    tags: List[str] = []    # 리스트도 각 원소까지 검사 됨 

# 중첩 dict를 넣으면 Pydantic이 알아서 Seller로 변환 + 검증
p = Product(id=1, price=100, seller={'seller_id': 9, 'region': 'KR'})
print(p.seller.region)    # KR

# STEP 5 : 40건을 돌리며 유효/무효로 나누기 - 이 실습의 목적지 
# 한 건이 실패해도 멈추면 안 됨
# 실패는 기록하고 다음 건으로 넘어가야 40건을 다 검사할 수 있음

from pydantic import ValidationError

valid, invalid = [], []

for i, row in enumerate(data):
    try:
        valid.append(Product(**row))  # 통과!
    except ValidationError as e:
        invalid.append({              # 탈락 - 이유까지 저장  
            'index': i,               
            'data': row, 
            'errors' : e.errors(),    # 어떤 필드가 왜 틀렸는지
        })

print(f'전체 {len(data)}건 -> 유효 {len(valid)} / 오염 {len(invalid)}')
# 40건 -> 유효 36 / 오염 4가 나와야 성공 

# STEP 6: 탈락 사유를 표로 출력 (확장 과제)

print(f"{'행':<4}{'필드':<12}{'사유'}")
for item in invalid:
    for err in item['errors']:
        field = '.'.join(str(x) for x in err['loc']) # 중첩 경로 표시
        print(f"{item['index']:<4}{field:<12}{err['msg']}")